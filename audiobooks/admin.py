from django.contrib import admin

from audiobooks.models import *


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')


class BookAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    list_filter = ('genre', 'language')


class FileAdmin(admin.ModelAdmin):
    list_display = ('book', 'file_name',)
    ordering = ('file_name',)


admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Author, AuthorAdmin)
admin.site.register(AudioBook, BookAdmin)
admin.site.register(AudioFile, FileAdmin)
admin.site.register(TorrentFile)

