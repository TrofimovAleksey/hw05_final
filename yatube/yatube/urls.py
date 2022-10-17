"""yatube URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("", include("posts.urls", namespace="posts")),
    # приложение about
    path("about/", include("about.urls", namespace="about")),
    # админка
    path("admin/", admin.site.urls),
    # Django проверяет url-адреса сверху вниз,
    # нам нужно, чтобы Django сначала проверял адреса в приложении users
    path("auth/", include("users.urls")),
    # Если какой-то URL не обнаружится в приложении users -
    # Django пойдёт искать его в django.contrib.auth
    path("auth/", include("django.contrib.auth.urls")),
]

handler404 = "core.views.page_not_found"

# Эта колдограмма будет работать, когда ваш сайт в режиме отладки.
# Он позволяет обращаться к файлам в директории, указанной в MEDIA_ROOT
# по имени, через префикс MEDIA_URL.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
