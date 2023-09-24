from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import (HTTP_201_CREATED, HTTP_204_NO_CONTENT,
                                   HTTP_400_BAD_REQUEST)


def add_remove(self, request, target, obj, target_obj):

    success_delete = {
        'detail': f"Success delete from your {obj.__name__}'s list"}
    already_in_list = {'errors': f"Already in your {obj.__name__}'s list"}
    not_in_list = {'errors': f"Not in your {obj.__name__}'s list"}

    user = self.request.user
    get_obj = get_object_or_404(target_obj, pk=self.kwargs.get(target))
    target_kwargs = {
        'user': user,
        target: get_obj
    }
    filtered = obj.objects.filter(**target_kwargs)

    if request.method == 'POST' and filtered.exists():
        return Response(already_in_list, status=HTTP_400_BAD_REQUEST)
    if request.method == 'POST':
        obj.objects.create(**target_kwargs)
        serializer = self.serializer_class(get_obj)
        return Response(serializer.data, status=HTTP_201_CREATED)

    if request.method == 'DELETE' and filtered.exists():
        filtered.delete()
        return Response(success_delete, status=HTTP_204_NO_CONTENT)
    if request.method == 'DELETE':
        return Response(not_in_list, status=HTTP_400_BAD_REQUEST)

    return True
