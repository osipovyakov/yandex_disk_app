import requests
from django.shortcuts import render, redirect


def start_page(request):
    """
    Представление для отображения стартовой страницы с формой для ввода public_key.
    """
    if request.method == 'POST':
        public_key = request.POST.get('public_key')
        if public_key:
            # Сохраняем public_key в сессии
            request.session['public_key'] = public_key
            return redirect('auth_app:oauth_login')  # Перенаправляем на авторизацию
        else:
            return render(request, 'disk_app/home.html', {'error': 'Введите public_key.'})
    return render(request, 'disk_app/home.html')


def file_list(request):
    """
    Основное представление для отображения файлов на Яндекс.Диске.
    """
    public_key = request.GET.get('public_key')
    if not public_key:
        return redirect('disk_app:start_page')  # Перенаправьте пользователя на стартовую страницу для ввода public_key

    access_token = request.session.get('access_token')
    if not access_token:
        # Сохраните public_key в сессии, чтобы использовать его после авторизации
        request.session['public_key'] = public_key
        return redirect('auth_app:oauth_login')  # Перенаправьте пользователя на страницу авторизации

    headers = {'Authorization': f'OAuth {access_token}'}

    url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        files = response.json().get('_embedded', {}).get('items', [])

        file_type = request.GET.get('file_type', 'all')
        # Применение фильтра
        if file_type == 'documents':
            files = [f for f in files if f.get('mime_type', '').startswith('application/')]
        elif file_type == 'images':
            files = [f for f in files if f.get('mime_type', '').startswith('image/')]
        elif file_type == 'videos':
            files = [f for f in files if f.get('mime_type', '').startswith('video/')]
        elif file_type == 'audio':
            files = [f for f in files if f.get('mime_type', '').startswith('audio/')]
        elif file_type == 'archives':
            files = [f for f in files if f.get('mime_type', '').startswith('application/zip') or 
                                          f.get('mime_type', '').startswith('application/x-rar-compressed')]
        elif file_type == 'others':
            files = [f for f in files if not (f.get('mime_type', '').startswith('application/') or 
                                              f.get('mime_type', '').startswith('image/') or 
                                              f.get('mime_type', '').startswith('video/') or 
                                              f.get('mime_type', '').startswith('audio/'))]

        return render(request, 'disk_app/file_list.html', {'files': files, 'file_type': file_type})
    else:
        return render(request, 'disk_app/error.html', {'message': 'Ошибка при получении списка файлов.'})

def download_file(request, file_path):
    """
    Представление для загрузки файла с Яндекс.Диска.
    """
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect('auth_app:oauth_login')  # Перенаправьте пользователя на страницу авторизации

    headers = {'Authorization': f'OAuth {access_token}'}
    response = requests.get('https://cloud-api.yandex.net/v1/disk', headers=headers)
    download_url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path=public_folder{file_path}'
    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        download_link = response.json().get('href')
        return redirect(download_link)
    else:
        return render(request, 'disk_app/error.html', {'message': 'Ошибка при получении ссылки для загрузки файла.'})
