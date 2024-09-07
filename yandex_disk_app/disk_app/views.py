import os
import io
import zipfile
import requests
from typing import List, Optional, Union
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from .file_filter import filter_files


def start_page(request: HttpRequest) -> Union[TemplateResponse, HttpResponse]:
    """Представление для отображения стартовой страницы с формой для ввода public_key"""
    if request.method == 'POST':
        public_key: Optional[str]= request.POST.get('public_key')
        if public_key:
            # Сохраняем public_key в сессии
            request.session['public_key'] = public_key
            # Перенаправляем на авторизацию
            return redirect('auth_app:oauth_login')
        else:
            return render(request, 'disk_app/home.html', {'error': 'Введите public_key'})
    return render(request, 'disk_app/home.html')


def file_list(request: HttpRequest) -> Union[TemplateResponse, HttpResponse]:
    """Основное представление для отображения файлов на Яндекс.Диске"""
    public_key: Optional[str] = request.GET.get('public_key')
    if not public_key:
        # Перенаправляем пользователя на стартовую страницу для ввода public_key
        return redirect('disk_app:start_page')  

    access_token: Optional[str]= request.session.get('access_token')
    if not access_token:
        # Сохраняем public_key в сессии, чтобы использовать его после авторизации
        request.session['public_key'] = public_key
        # Перенаправляем пользователя на страницу авторизации
        return redirect('auth_app:oauth_login')

    headers = {'Authorization': f'OAuth {access_token}'}

    url = f'https://cloud-api.yandex.net/v1/disk/public/resources?public_key={public_key}'
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        files = response.json().get('_embedded', {}).get('items', [])

        file_type: str = request.GET.get('file_type', 'all')
        # Добавляем фильтрацию файлов по типу
        files = filter_files(files, file_type)

        return render(request, 'disk_app/file_list.html', {'files': files, 'file_type': file_type})
    else:
        return render(request, 'disk_app/error.html', {'message': 'Ошибка при получении списка файлов'})


def download_file(request: HttpRequest, file_path: str) -> HttpResponse:
    """Представление для загрузки файла с Яндекс.Диска"""
    access_token: Optional[str] = request.session.get('access_token')
    if not access_token:
        # Перенаправляем пользователя на страницу авторизации
        return redirect('auth_app:oauth_login')

    headers = {'Authorization': f'OAuth {access_token}'}
    response = requests.get('https://cloud-api.yandex.net/v1/disk', headers=headers)
    download_url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path=public_folder{file_path}'
    response = requests.get(download_url, headers=headers)
    if response.status_code == 200:
        download_link: str = response.json().get('href')
        return redirect(download_link)
    else:
        return render(request, 'disk_app/error.html', {'message': 'Ошибка при получении ссылки для загрузки файла'})


def download_multiple_files(request: HttpRequest) -> HttpResponse:
    """Представление для скачивания нескольких файлов с Яндекс.Диска"""
    # Получаем список путей к файлам
    file_paths: Optional[List] = request.POST.getlist('selected_files')
    access_token: Optional[str] = request.session.get('access_token')
    
    if not access_token:
        return redirect('auth_app:oauth_login')

    if not file_paths:
        return render(request, 'disk_app/error.html', {'message': 'Вы не выбрали ни одного файла'})
    
    headers = {'Authorization': f'OAuth {access_token}'}
    
    # Создаем архив для нескольких файлов
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file_path in file_paths:
            download_url = f'https://cloud-api.yandex.net/v1/disk/resources/download?path=public_folder{file_path}'
            response = requests.get(download_url, headers=headers)
            
            if response.status_code == 200:
                download_link: str = response.json().get('href')
                file_content = requests.get(download_link).content
                file_name: str = os.path.basename(file_path)
                # Добавляем файл в архив
                zip_file.writestr(file_name, file_content)
            else:
                return render(request, 'disk_app/error.html', {'message': f'Ошибка при загрузке файла {file_path}'})
    
    # Подготавливаем ответ с архивом
    zip_buffer.seek(0)
    response = HttpResponse(zip_buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="files.zip"'
    return response
