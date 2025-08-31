from django import forms
from .models import Quote, Source, SourceType


class QuoteForm(forms.ModelForm):
    # Поля для создания нового источника, если его нет в базе
    new_source_title = forms.CharField(
        max_length=200,
        required=False,
        label='Новый источник (если нет в списке)',
        help_text='Введите название нового источника'
    )

    new_source_type = forms.ChoiceField(
        choices=SourceType.choices,
        required=False,
        label='Тип нового источника'
    )

    class Meta:
        model = Quote
        fields = ['text', 'source', 'weight']
        labels = {
            'text': 'Текст цитаты',
            'source': 'Выберите источник',
            'weight': 'Вес цитаты',
        }
        help_texts = {
            'weight': 'Чем выше вес, тем чаще показывается цитата (минимум 1)',
        }
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор только теми источниками, у которых меньше 3 цитат
        self.fields['source'].queryset = Source.objects.filter(quote_count__lt=3)

        # Если нет источников с доступными местами, скрываем поле выбора
        if not self.fields['source'].queryset.exists():
            self.fields['source'].widget = forms.HiddenInput()
            self.fields['source'].required = False

    def clean(self):
        cleaned_data = super().clean()
        text = cleaned_data.get('text')
        source = cleaned_data.get('source')
        new_source_title = cleaned_data.get('new_source_title')
        new_source_type = cleaned_data.get('new_source_type')

        # Проверяем, что выбран либо существующий источник, либо указаны данные для нового
        if not source and not (new_source_title and new_source_type):
            raise forms.ValidationError(
                'Выберите существующий источник или укажите данные для нового'
            )

        # Если указан новый источник, проверяем его данные
        if new_source_title and new_source_type:
            # Проверяем, не существует ли уже источник с таким названием
            if Source.objects.filter(title__iexact=new_source_title.strip()).exists():
                raise forms.ValidationError(
                    f'Источник "{new_source_title}" уже существует. Выберите его из списка.'
                )

        # Проверяем дубликаты цитат
        if text and source:
            if Quote.objects.filter(text__iexact=text.strip(), source=source).exists():
                raise forms.ValidationError(
                    'Такая цитата уже существует для этого источника'
                )

        return cleaned_data

    def save(self, commit=True):
        # Если указан новый источник, создаем его
        new_source_title = self.cleaned_data.get('new_source_title')
        new_source_type = self.cleaned_data.get('new_source_type')

        if new_source_title and new_source_type:
            source = Source.objects.create(
                title=new_source_title.strip(),
                type=new_source_type
            )
            self.cleaned_data['source'] = source

        return super().save(commit=commit)