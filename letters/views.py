from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import LetterRequest, LetterType, GeneratedLetter
from .forms import LetterRequestForm
from residents.models import Resident
from utils.email_utils import send_letter_approval_notification
from utils.decorators import role_required, rate_limit, log_activity
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io
import logging

logger = logging.getLogger('ward_system')

@login_required
@role_required(['resident'])
# 10 requests per hour for authenticated users, 3 for anonymous
@rate_limit('letter_request', limit=10, window=3600)
@log_activity('letter_request')
def letter_request(request):
    
    try:
        resident = request.user.resident
    except Resident.DoesNotExist:
        messages.error(request, 'Please complete your resident registration first.')
        return redirect('residents:register')
    
    # If no letter types are configured, avoid rendering an empty select
    if not LetterType.objects.exists():
        messages.info(request, 'Letter request types are not configured yet. Please try again later.')
        return redirect('home')

    if request.method == 'POST':
        form = LetterRequestForm(request.POST)
        if form.is_valid():
            letter_request = form.save(commit=False)
            letter_request.resident = resident
            letter_request.requested_by = request.user
            letter_request.save()
            messages.success(request, 'Letter request submitted successfully!')
            return redirect('letters:my_requests')
    else:
        form = LetterRequestForm()
    
    return render(request, 'letters/request.html', {'form': form})

@login_required
def my_requests(request):
    if request.user.role != 'resident':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Get all requests for the current user with related data to reduce queries
    requests = LetterRequest.objects.filter(
        requested_by=request.user
    ).select_related('letter_type').order_by('-request_date')
    
    # Check for any letter_approved messages and update the session
    storage = messages.get_messages(request)
    letter_approved = False
    for message in storage:
        if hasattr(message, 'extra_tags') and 'letter_approved' in message.extra_tags:
            letter_approved = True
            break
    
    # Clear the messages to prevent duplicates
    storage.used = True
    
    # Add a success message if a letter was just approved
    if letter_approved:
        messages.success(
            request,
            'Your letter has been approved! You can now download it below.',
            extra_tags='letter_approved_alert'
        )
    
    # Paginate the results
    paginator = Paginator(requests, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'letters/my_requests.html', {
        'requests': page_obj,
        'letter_approved': letter_approved
    })

@login_required
def pending_requests(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    requests = LetterRequest.objects.filter(status='pending').select_related('resident', 'letter_type').order_by('-request_date')
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    requests = paginator.get_page(page_number)
    
    return render(request, 'letters/pending.html', {'requests': requests})

@login_required
def all_requests(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    requests = LetterRequest.objects.all().select_related('resident', 'letter_type').order_by('-request_date')
    paginator = Paginator(requests, 20)
    page_number = request.GET.get('page')
    requests = paginator.get_page(page_number)
    
    return render(request, 'letters/all.html', {'requests': requests})

@login_required
def request_detail(request, pk):
    letter_request = get_object_or_404(LetterRequest, pk=pk)
    
    # Check permissions
    if request.user.role == 'resident' and letter_request.requested_by != request.user:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'letters/detail.html', {'letter_request': letter_request})

@login_required
@role_required(['admin'])
@log_activity('approve_letter_request')
def approve_request(request, pk):
    
    letter_request = get_object_or_404(LetterRequest, pk=pk)
    
    if request.method == 'POST':
        admin_notes = request.POST.get('admin_notes', '')
        letter_request.status = 'approved'
        letter_request.approval_date = timezone.now()
        letter_request.approved_by = request.user
        letter_request.admin_notes = admin_notes
        letter_request.save()
        
        # Send email notification
        try:
            send_letter_approval_notification(letter_request)
            logger.info(f'Approval notification sent for letter request {letter_request.id}')
            # Add success message for the admin
            messages.success(request, f'Letter request for {letter_request.resident.full_name} has been approved and notification sent.')
            
            # Add success message that will be shown to the resident
            from django.contrib import messages as msg
            from django.contrib.messages import get_messages
            
            # Store a message for the resident
            storage = get_messages(request)
            storage.used = True  # Mark existing messages as used
            msg.success(
                request, 
                f'Your {letter_request.letter_type.name} request has been approved! You can now download your letter.',
                extra_tags='letter_approved'
            )
        except Exception as e:
            logger.error(f'Failed to send approval notification: {e}')
            messages.warning(request, f'Letter was approved but could not send notification: {e}')
        return redirect('letters:detail', pk=letter_request.pk)
    
    return render(request, 'letters/approve.html', {'letter_request': letter_request})

@login_required
def reject_request(request, pk):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    letter_request = get_object_or_404(LetterRequest, pk=pk)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        letter_request.status = 'rejected'
        letter_request.approved_by = request.user
        letter_request.approval_date = timezone.now()
        letter_request.rejection_reason = rejection_reason
        letter_request.save()
        
        messages.success(request, 'Letter request rejected.')
        return redirect('letters:detail', pk=pk)
    
    return render(request, 'letters/reject.html', {'letter_request': letter_request})

@login_required
def generate_pdf(request, pk):
    letter_request = get_object_or_404(LetterRequest, pk=pk, status='approved')
    
    # Allow admin or the resident who requested the letter to download
    if request.user.role != 'admin' and letter_request.requested_by != request.user:
        messages.error(request, 'Access denied. You can only download your own approved letters.')
        return redirect('home')
    
    # Create PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Official Letterhead
    p.setFont("Helvetica-Bold", 18)
    title = "WARD ADMINISTRATION OFFICE"
    title_width = p.stringWidth(title, "Helvetica-Bold", 18)
    p.drawString((width - title_width) / 2, height - 0.8*inch, title)
    
    # Ward details
    p.setFont("Helvetica", 10)
    ward_info = f"Ward: {letter_request.resident.household.ward}"
    ward_width = p.stringWidth(ward_info, "Helvetica", 10)
    p.drawString((width - ward_width) / 2, height - inch, ward_info)
    
    # Contact information
    contact_info = "Tel: +255 763 587 710 | Email: sarangakata@info.go.tz"
    contact_width = p.stringWidth(contact_info, "Helvetica", 10)
    p.drawString((width - contact_width) / 2, height - 1.2*inch, contact_info)
    
    # Reference number and date (right aligned)
    p.setFont("Helvetica", 11)
    ref_number = f"Reference No.: WRD/{letter_request.id:06d}/{timezone.now().year}"
    p.drawRightString(width - inch, height - 1.8*inch, ref_number)
    p.drawRightString(width - inch, height - 2*inch, f"Date: {timezone.now().strftime('%d %B %Y')}")
    
    # Subject line
    y_position = height - 2.5*inch
    p.setFont("Helvetica-Bold", 12)
    subject = f"RE: {letter_request.letter_type.name.upper()}"
    p.drawString(inch, y_position, subject)
    
    # Main content starts here
    y_position -= 0.5*inch
    p.setFont("Helvetica", 11)
    
    content_lines = [
        "TO WHOM IT MAY CONCERN",
        "",
        "Dear Sir/Madam,",
        "",
        f"RE: INTRODUCTION OF A RESIDENT {letter_request.resident.full_name.upper()}",
        "",
        "Please refer to letter head above,",
        "",
        f"2. Be informed that {letter_request.resident.full_name.upper()} with national identity number(NIDA) {letter_request.resident.nida_number} is a",
        f"   resident at {letter_request.resident.household.ward}, at saranga ward. He/She is pursuing {letter_request.purpose}.",
        f"   He/She has been registered in our ward.",
        "",
        "3. We request your good office to assist the resident where he/she need arises.",
        "",
        "4. If there is any question, please don't hesitate to ask.",
        "",
        "5. Yours in Public Service,",
        "",
        "",
        "________________________",
        "Ward Executive Officer",
        f"For {letter_request.resident.household.ward}",
        "RESIDENT CONTACTS:",
        f"Phone Number: {letter_request.resident.phone_number or 'Not provided'}",
        f"Current Address: {letter_request.resident.household.house_number}, {letter_request.resident.household.street_name}",
    ]
    
    for line in content_lines:
        p.drawString(inch, y_position, line)
        y_position -= 20
    
    p.showPage()
    p.save()
    
    # Update request status
    letter_request.status = 'completed'
    letter_request.completion_date = timezone.now()
    letter_request.save()
    
    # Create GeneratedLetter record
    GeneratedLetter.objects.create(
        letter_request=letter_request,
        content="\n".join(content_lines),
        generated_by=request.user
    )
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    # Use resident's full name for filename
    safe_name = letter_request.resident.full_name.replace(' ', '_').replace('.', '')
    response['Content-Disposition'] = f'attachment; filename="{safe_name}_Introduction_Letter.pdf"'
    
    return response
