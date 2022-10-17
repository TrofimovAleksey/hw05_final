from django.forms import ModelForm, Textarea

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        # На основе какой модели создаётся класс формы
        model = Post
        # Укажем, какие поля будут в форме
        fields = ("text", "group", "image")
        widgets = {
            "text": Textarea(attrs={"cols": 40, "rows": 10}),
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
