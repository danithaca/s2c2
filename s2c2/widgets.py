from django.forms import CheckboxSelectMultiple, widgets
from django.forms.widgets import ChoiceFieldRenderer, CheckboxFieldRenderer
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class InlineCheckboxFieldRenderer(CheckboxFieldRenderer):

    def render(self):
        """
        Outputs a <ul> for this set of choice fields.
        If an id was given to the field, it is applied to the <ul> (each
        item in the list will get an id of `$id_$i`).
        """
        id_ = self.attrs.get('id', None)
        # this is the only place that changes.
        start_tag = format_html('<ul id="{0}" class="list-inline">', id_) if id_ else '<ul>'
        output = [start_tag]
        for i, choice in enumerate(self.choices):
            choice_value, choice_label = choice
            if isinstance(choice_label, (tuple, list)):
                attrs_plus = self.attrs.copy()
                if id_:
                    attrs_plus['id'] += '_{0}'.format(i)
                sub_ul_renderer = ChoiceFieldRenderer(name=self.name,
                                                      value=self.value,
                                                      attrs=attrs_plus,
                                                      choices=choice_label)
                sub_ul_renderer.choice_input_class = self.choice_input_class
                output.append(format_html('<li>{0}{1}</li>', choice_value,
                                          sub_ul_renderer.render()))
            else:
                w = self.choice_input_class(self.name, self.value,
                                            self.attrs.copy(), choice, i)
                output.append(format_html('<li>{0}</li>', force_text(w)))
        output.append('</ul>')
        return mark_safe('\n'.join(output))


class InlineCheckboxSelectMultiple(CheckboxSelectMultiple):
    renderer = InlineCheckboxFieldRenderer


class USPhoneNumberWidget(widgets.TextInput):

    def __init__(self, attrs=None):
        if attrs is not None:
            if 'class' in attrs and len(attrs['class']) > 0:
                attrs['class'] += ' phone-number'
            else:
                attrs['class'] = 'phone-number'
        else:
            attrs = {'class': 'phone-number'}
        super(USPhoneNumberWidget, self).__init__(attrs)

    class Media:
        js = (r'http://firstopinion.github.io/formatter.js/javascripts/formatter.min.js', 'js/phone_number_widget.js')