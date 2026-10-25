from django import forms
from .models import Subject, Report

class SubjectForm(forms.ModelForm):
  
    class Meta:
        model = Subject
        fields = ['title', 'abstract', 'keywords']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 transition text-sm',
                'placeholder': 'Ex: Plateforme de gestion intelligente'
            }),
            'abstract': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 transition text-sm',
                'placeholder': 'Décrivez en détail la problématique'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 transition text-sm',
                'placeholder': 'Ex: Django'
            }),
        }


class ReportUploadForm(forms.ModelForm):
  
    class Meta:
        model = Report
        fields = ['file', 'description']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 transition text-sm file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-emerald-500 file:text-white hover:file:bg-emerald-600'
            }),
            'description': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-4 py-3 rounded-xl bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-emerald-500 transition text-sm',
                'placeholder': 'Description de l’envoi à destination de l’encadrant...'
            }),
        }