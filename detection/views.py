from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.conf import settings
import base64
import os

from .utils import predict_fire, predict_fire_from_video, predict_fire_from_video
from .models import DetectionHistory

import requests

def get_ip_and_location(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()

        return {
            'ip': ip,
            'latitude': data.get('lat'),
            'longitude': data.get('lon'),
            'city': data.get('city'),
            'country': data.get('country')
        }
    except:
        return {
            'ip': ip,
            'latitude': None,
            'longitude': None,
            'city': None,
            'country': None
        }


@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)

        result = predict_fire(fs.path(filename))

        lokasi = get_ip_and_location(request)
        DetectionHistory.objects.create(
            filename=image.name,
            url=fs.url(filename),
            result=result,
            ip_address=lokasi['ip'],
            city=lokasi['city'],
            country=lokasi['country'],
            latitude=lokasi['latitude'],
            longitude=lokasi['longitude'],
        )

        return JsonResponse({"result": result, "url": fs.url(filename)})
    return JsonResponse({"error": "Invalid request"}, status=400)


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from .models import DetectionHistory

@csrf_exempt
def upload_video(request):
    if request.method == "POST" and request.FILES.get("video"):
        video = request.FILES["video"]
        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        video_url = fs.url(filename)

        result = predict_fire_from_video(fs.path(filename))

        lokasi = get_ip_and_location(request)
        DetectionHistory.objects.create(
            filename=video.name,
            url=video_url,
            result=result,
            ip_address=lokasi['ip'],
            city=lokasi['city'],
            country=lokasi['country'],
            latitude=lokasi['latitude'],
            longitude=lokasi['longitude'],
        )

        return JsonResponse({
            "result": result,
            "url": video_url
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def detect_fire_camera(request):
    if request.method == "POST":
        data_url = request.POST.get("image")

        if not data_url:
            return JsonResponse({"error": "No image data"}, status=400)

        try:
            header, encoded = data_url.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            img = Image.open(BytesIO(img_bytes))

            if img.mode == 'RGBA':
                img = img.convert('RGB')

            filename = f"camera_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            save_path = os.path.join(settings.MEDIA_ROOT, filename)
            img.save(save_path)

            result = predict_fire(save_path)

            url = os.path.join(settings.MEDIA_URL, filename)

            lokasi = get_ip_and_location(request)
            DetectionHistory.objects.create(
                filename=filename,
                url=url,
                result=result,
                ip_address=lokasi['ip'],
                city=lokasi['city'],
                country=lokasi['country'],
                latitude=lokasi['latitude'],
                longitude=lokasi['longitude'],
            )

            return JsonResponse({"result": result, "url": url})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid method"}, status=405)
    
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import DetectionHistory
from .utils import predict_fire
import os
from django.core.files.storage import default_storage

@csrf_exempt
def detect_file_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_path = default_storage.save('uploads/' + uploaded_file.name, uploaded_file)
        full_path = os.path.join(default_storage.location, file_path)

        # Deteksi kebakaran
        result = predict_fire(full_path)

        # Simpan ke database
        DetectionHistory.objects.create(image=file_path, result=result)

        return JsonResponse({'result': result})
    return JsonResponse({'error': 'File tidak ditemukan'}, status=400)



def index(request):
    histories = DetectionHistory.objects.all().order_by('-timestamp')
    latest_result = histories[0].result if histories else "No detection"
    context = {
        'histories': histories,
        'result': latest_result,
    }
    return render(request, 'index.html', context)


def detection_view(request):
    last_detection = DetectionHistory.objects.order_by('-timestamp').first()
    result = last_detection.result if last_detection else "No detection yet"

    context = {
        "result": result,
    }
    return render(request, "index.html", context)




def history(request):
    histories = DetectionHistory.objects.all().order_by('-timestamp')
    return render(request, 'history.html', {'histories': histories})

def save_prediction_to_db(predicted_label, confidence):
    DetectionHistory.objects.create(
        result=f"{predicted_label} ({confidence:.2f})"
    )

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def delete_history(request, id):
    if request.method == "POST":
        history = get_object_or_404(DetectionHistory, id=id)
        history.delete()
    return redirect('history_page')

def delete_all_history(request):
    for history in DetectionHistory.objects.all():
        history.delete()
    return redirect('history_page')

def delete_selected_history(request):
    if request.method == 'POST':
        selected_ids = request.POST.getlist('selected_ids')
        for history in DetectionHistory.objects.filter(id__in=selected_ids):
            history.delete()
    return redirect('history_page')

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Jawaban chatbot rule-based
RESPONSES = {
    "apa itu fireguard": "FireGuard adalah sistem deteksi kebakaran berbasis AI.",
    "bagaimana cara pakai": "Upload gambar dan sistem akan mendeteksi kebakaran secara otomatis.",
    "apakah gratis": "Sistem ini gratis untuk penggunaan dasar.",
    "siapa pembuatnya": "Sistem ini dibuat oleh tim pengembang FireGuard.",
}

def get_bot_response(message):
    message = message.lower()
    for key in RESPONSES:
        if key in message:
            return RESPONSES[key]
    return "Maaf, saya tidak mengerti pertanyaan Anda. Silakan coba tanya yang lain ya."

@csrf_exempt  # supaya bisa POST dari JS tanpa token CSRF (untuk contoh sederhana)
def chat_view(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")
        bot_reply = get_bot_response(user_message)
        return JsonResponse({"reply": bot_reply})
    return render(request, "chat.html")
