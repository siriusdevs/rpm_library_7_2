from django.shortcuts import render
from .models import Book, Genre, Author
from django.views.generic import ListView
from django.core.paginator import Paginator
from rest_framework.viewsets import ModelViewSet
from .serializers import BookSerializer, AuthorSerializer, GenreSerializer
from rest_framework.permissions import BasePermission, IsAuthenticated


PAGINATOR_THRESHOLD = 20
TEMPLATE_MAIN = 'index.html'

def custom_main(request):
    return render(
        request,
        TEMPLATE_MAIN,
        context={
            'books': Book.objects.all().count(),
            'genres': Genre.objects.all().count(),
            'authors': Author.objects.all().count(),
        }
    )

def catalog_view(cls_model, context_name, template):
    class CustomListView(ListView):
        model = cls_model
        template_name = template
        paginate_by = PAGINATOR_THRESHOLD
        context_object_name = context_name

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            objects = cls_model.objects.all()
            paginator = Paginator(objects, PAGINATOR_THRESHOLD)
            page = self.request.GET.get('page')
            page_obj = paginator.get_page(page)
            context[f'{context_name}_list'] = page_obj
            return context

    return CustomListView

def entity_view(cls_model, name, template):
    def view(request):
        return render(
            request,
            template,
            context={
                name: cls_model.objects.get(id=request.GET.get('id', ''))
            }
        )
    return view

CATALOG = 'catalog'
BOOKS_CATALOG = f'{CATALOG}/books.html'
AUTHORS_CATALOG = f'{CATALOG}/authors.html'
GENRES_CATALOG = f'{CATALOG}/genres.html'

BookListView = catalog_view(Book, 'books', BOOKS_CATALOG)
AuthorListView = catalog_view(Author, 'authors', AUTHORS_CATALOG)
GenreListView = catalog_view(Genre, 'genres', GENRES_CATALOG)

ENTITIES = 'entities'
BOOK_ENTITY = f'{ENTITIES}/book.html'
AUTHOR_ENTITY = f'{ENTITIES}/author.html'
GENRE_ENTITY = f'{ENTITIES}/genre.html'

book_view = entity_view(Book, 'book', BOOK_ENTITY)
genre_view = entity_view(Genre, 'genre', GENRE_ENTITY)
author_view = entity_view(Author, 'author', AUTHOR_ENTITY)


class Permission(BasePermission):
    def has_permission(self, request, _):
        if request.method == 'GET':
            return bool(request.user and request.user.is_authenticated)
        elif request.method == 'POST' or request.method == 'DELETE':
            return bool(request.user and request.user.is_superuser)
        return False

def create_viewset(cls_model, serializer, order_field):
    class CustomViewSet(ModelViewSet):
        queryset = cls_model.objects.all()
        serializer_class = serializer
        permission_classes = [Permission]

        def get_queryset(self):
            queryset = cls_model.objects.all()
            query = {}
            for field in serializer.Meta.fields:
                value = self.request.GET.get(field, '')
                if value:
                    query[field] = value
            if query:
                queryset = queryset.filter(**query)
            return queryset.order_by(order_field)


    return CustomViewSet

BookViewSet = create_viewset(Book, BookSerializer, 'title')
AuthorViewSet = create_viewset(Author, AuthorSerializer, 'full_name')
GenreViewSet = create_viewset(Genre, GenreSerializer, 'name')
