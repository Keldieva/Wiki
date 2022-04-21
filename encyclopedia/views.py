from audioop import reverse
import random
from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from markdown2 import Markdown
from django import forms
from . import util
from django.contrib import messages
from django.http import Http404
import re


class NewEntryForm(forms.Form):
    title = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": "Title", "class": "mb-4"}
        ),
    )
    content = forms.CharField(
        required=True,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-4",
                "placeholder": "Content",
                "id": "new_content",
            }
        )
    )


class SearchForm(forms.Form):
    title = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "search",
                "placeholder": "Search Wiki"
            }
        )
    )


class CreateForm(forms.Form):
    title = forms.CharField(label="Title")
    textarea = forms.CharField(widget=forms.Textarea(), label='')


def index(request):

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_form": SearchForm()
    })


def entries(request, entry):
    if entry not in util.list_entries():
        raise Http404
    content = util.get_entry(entry)

    return render(
        request,
        "encyclopedia/wiki.html",
        {"title": entry, "content": Markdown().convert(content)},
    )


def add(request):
    if request.method == "GET":
        return render(request, "encyclopedia/add.html", {
            "form": NewEntryForm(),
            "search": SearchForm()
        })

    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.data.get("title")
            content = form.data.get("content")

            if title.lower() in [entry_name.lower() for entry_name in util.list_entries()]:
                messages.add_message(
                    request,
                    messages.WARNING,
                    message=f'Entry "{title}" already exists',
                )
            else:
                with open(f"entries/{title}.md", "w") as file:
                    file.write(f"# {title}\n")
                    file.write(content)

                return redirect(reverse('entries', args=[title]))

        else:
            return render(request, "encyclopedia/add.html")

    else:
        messages.add_message(request, messages.WARNING, message="Invalid request form")


def wiki(request):
    if entries not in util.list_entries():
        raise Http404
    content = util.get_entry(entries)

    return render(
        request,
        "encyclopedia/wiki.html",
        {"title": entries, "content": Markdown().convert(content)},
    )


def change(request, title):
    if request.method == "GET":
        text = util.get_entry(title)
        form = NewEntryForm({"title": title, "content": text})

        return render(request, "encyclopedia/change.html", {
            "form": form,
            "title": title
        })

    if request.method == "POST":
        form = NewEntryForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data.get("title")
            content = form.cleaned_data.get("content")
            util.save_entry(title=title, content=content)
            messages.success(request, f'Entry "{entries}" updated successfully!')

            return redirect(reverse('entries', args=[title]))

        else:
            title = entry
            messages.error(request, f'Editing form not valid, please try again!')
            return render(request, "encyclopedia/change.html", {
                "title": title,
                "edit_form": form,
                "search_form": SearchForm()
            })


def entry(request, name):
    """
    Renders HTML entry page
    """
    entry = util.get_entry(name)
    if not entry:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    # convert markdown into HTML
    entry = Markdown.convert(entry)

    return render(request, "encyclopedia/entry.html", {
        "name": name,
        "entry": entry
    })


def search(request):
    """
    Search by title. Redirects to a search results page or, if a complete match, to
    an entry page
    """
    title = request.POST.get('q')
    entry = util.get_entry(title)
    list_titles = util.list_entries()

    if entry:
        # convert markdown into HTML
        entries = Markdown.convert(entry)

        return redirect("entry", title)

    result = []
    for item in list_titles:
        if re.search(title, item, re.IGNORECASE):
            result.append(item)

    return render(request, "encyclopedia/search.html", {
        "name": title,
        "entries": result
    })


def random_page(request):
    # Get list of titles, pick one at random:
    titles = util.list_entries()
    title = random.choice(titles)

    # Redirect to selected page:
    return redirect(reverse('entries', args=[title]))
