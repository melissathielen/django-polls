import datetime
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, CheckboxInput
from polls.models import Poll, Answer


class BaseAnswerEditFormSet(BaseInlineFormSet):
    def save(self, commit=True):
        f = super(BaseAnswerEditFormSet, self).save()
        print 'save'
        print self.cleaned_data

AnswerEditFormSet = inlineformset_factory(Poll, Answer, fields=('text','id',), extra=4, max_num=10, formset=BaseAnswerEditFormSet)

class PollEditForm(forms.ModelForm):
    
    NUMBER_OF_SELECTIONS = (
        (0, 'No Limit'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
        (6, '6'),
        (7, '7'),
        (8, '8'),
        (9, '9'),
        (10, '10'),
    )
    
    allow_multiple_selections = forms.BooleanField(required=False)
    number_selections_allowed = forms.ChoiceField(choices=NUMBER_OF_SELECTIONS)
    
    def __init__(self, *args, **kwargs):

        super(PollEditForm, self).__init__(*args, **kwargs)
        
        #initialize number of selections
        if self.instance.number_answers_allowed != 1:
            self.fields['number_selections_allowed'].initial = self.instance.number_answers_allowed
            self.fields['allow_multiple_selections'].initial = True        
    
    class Meta:
        model = Poll
        exclude = ('author', 'site', 'number_answers_allowed')
        widgets = {
            'results_displayed': forms.RadioSelect(),
        } 
    
    def save(self, commit=True):
        
        p = super(PollEditForm, self).save(commit=False)

        #set number answers allowed
        if self.cleaned_data['allow_multiple_selections']:
            p.number_answers_allowed = self.cleaned_data['number_selections_allowed']
        else:
            p.number_answers_allowed = 1
        
        if commit:
            p.save()
            
        return p
        
    def clean(self):
        cleaned_data = super(PollEditForm, self).clean()
        question = cleaned_data.get('question')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if not question:
            self._errors['question'] = self.error_class([u'Question field cannot be blank'])
        
        if not start_date:
            self._errors['start_date'] = self.error_class([u'Start date field cannot be blank'])
        
        if not end_date:
            self._errors['end_date'] = self.error_class([u'End date field cannot be blank'])
                
        return cleaned_data
        

class VotingRadioForm(forms.Form):
    answers = forms.ChoiceField(widget=RadioSelect, required=True)
    user_answer = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):

        choices = kwargs.pop('choices', None)
        user_input_allowed = kwargs.pop('user_input', False)
        super(VotingRadioForm, self).__init__(*args, **kwargs)
        
        if choices:     
            self.fields['answers'].choices = choices
            
        if user_input_allowed:
            self.fields['answers'].choices.append(('0', 'Other'))
        else:
            self.fields['user_answer'].widget = forms.HiddenInput()
            
    def clean(self):
        cleaned_data = super(VotingRadioForm, self).clean()
        answers = cleaned_data.get('answers')
        
        if not answers:
            raise forms.ValidationError('You must select a choice')
        
        return cleaned_data   
    
class VotingCheckboxForm(forms.Form):
    answers = forms.MultipleChoiceField(widget=CheckboxSelectMultiple, required=True)
    user_answer = forms.CharField(required=False)
    
    def __init__(self, *args, **kwargs):

        choices = kwargs.pop('choices', None)
        selected_answers = kwargs.pop('selected_answers', None)
        user_input_allowed = kwargs.pop('user_input', False)
        #only needed for checkbox form
        self.allowed_answers = kwargs.pop('allowed_answers', 1)
        
        super(VotingCheckboxForm, self).__init__(*args, **kwargs)
        
        if choices:     
            self.fields['answers'].choices = choices
            #Used when errors occur, and selections need to remain
            self.fields['answers'].initial = selected_answers
        
        if user_input_allowed:
            self.fields['answers'].choices.append(('0', 'Others'))
        else:
            self.fields['user_answer'].widget = forms.HiddenInput()
            
    def clean(self):
        cleaned_data = super(VotingCheckboxForm, self).clean()
        answers = cleaned_data.get('answers')
        
        if not answers:
            raise forms.ValidationError('You didn\'t select a choice')
            
        #User entering other answer.
        if '0' in answers:
            #user input field is blank
            if not self.cleaned_data.get('user_answer'):
                raise forms.ValidationError('You need to enter an answer')
            
        if len(answers) >= self.allowed_answers:
            raise forms.ValidationError('You may only select %s answers. Remove additional selections and submit your vote.' % (self.allowed_answers))
        
        return cleaned_data
        
