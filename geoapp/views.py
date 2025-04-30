from django.shortcuts import render, redirect
from django.http import Http404
import json
from .models import Submission

def form_view(request):
    if request.method == 'POST':
        values = []
        for key, val in request.POST.items():
            if key.startswith('name'):
                values.append(val)
        area_coords = None
        if 'area' in request.POST and request.POST['area']:
            try:
                area_coords = json.loads(request.POST['area'])
            except json.JSONDecodeError:
                area_coords = None
        data = {"values": values}
        if area_coords:
            data["area"] = area_coords
        submission = Submission.objects.create(data=data)
        return redirect('result', id=submission.id)
    return render(request, 'geoapp/form.html')

def result_view(request, id):
    try:
        submission = Submission.objects.get(id=id)
    except Submission.DoesNotExist:
        raise Http404("Result not found")
    json_text = json.dumps(submission.data, ensure_ascii=False, indent=2)
    return render(request, 'geoapp/result.html', {
        'json_text': json_text,
        'area_json': json.dumps(submission.data.get("area", None))
    })
