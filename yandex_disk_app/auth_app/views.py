import requests
from django.conf import settings
from django.shortcuts import redirect, render
from django.urls import reverse

def oauth_login(request):
    """
    View для перенаправления пользователя на страницу авторизации Яндекс.ОAuth.
    """
    yandex_oauth_url = (
        f"https://oauth.yandex.ru/authorize?"
        f"response_type=code&client_id={settings.YANDEX_CLIENT_ID}&"
        f"redirect_uri={settings.YANDEX_REDIRECT_URI}"
    )
    return redirect(yandex_oauth_url)


def oauth_callback(request):
    """
    View для обработки редиректа после авторизации и получения access_token.
    """
    code = request.GET.get('code')

    if code:
        # Обмен кода авторизации на токен доступа
        token_url = "https://oauth.yandex.ru/token"
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': settings.YANDEX_CLIENT_ID,
            'client_secret': settings.YANDEX_CLIENT_SECRET,
            'redirect_uri': settings.YANDEX_REDIRECT_URI,
        }

        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            request.session['access_token'] = token_data['access_token']

            # Получаем сохраненный public_key из сессии
            public_key = request.session.get('public_key', '')
            
            # Редиректим на список файлов с public_key в URL
            return redirect(f'{reverse("disk_app:file_list")}?public_key={public_key}')
        else:
            return render(request, 'auth_app/error.html', {'message': 'Ошибка при обмене кода на токен доступа.'})
    else:
        return render(request, 'auth_app/error.html', {'message': 'Код авторизации не получен.'})
