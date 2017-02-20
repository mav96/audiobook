from django.db import models
import os


class Genre(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class Language(models.Model):
    lang = models.CharField(max_length=30)

    def __str__(self):
        return self.lang


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)

    def __str__(self):
        return u'%s %s' % (self.first_name, self.last_name)


class AudioBook(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    genre = models.ForeignKey(Genre, blank=True, null=True)
    language = models.ForeignKey(Language, blank=True, null=True)

    def __str__(self):
        return self.title


class AudioFile(models.Model):
    file_name = models.CharField(max_length=255, verbose_name='path to mp3 file')
    book = models.ForeignKey(AudioBook)

    def __str__(self):
        return os.path.basename(self.file_name)

    class Meta:
        ordering = ['file_name']