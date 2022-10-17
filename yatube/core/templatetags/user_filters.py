from django import template

# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляем к ним и наш фильтр.
register = template.Library()


@register.filter
def addclass(field, css):
    return field.as_widget(attrs={"class": css})


@register.filter
def string_30_char(field):
    data = (field[:30]) if len(field) > 30 else field
    return data


# синтаксис @register... , под который описана функция addclass() -
# это применение "декораторов", функций, меняющих поведение функций
# Не бойтесь соб@к
