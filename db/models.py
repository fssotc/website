from datetime import date

from django.db import models
from django.db.models.query_utils import Q
from django.core.exceptions import ValidationError

# Create your models here.


class Member(models.Model):
    name = models.CharField(max_length=40, verbose_name="Prénom / Name")
    family_name = models.CharField(max_length=40, verbose_name="Nom / Family Name")
    email = models.EmailField(unique=True, verbose_name="E-mail")
    phone = models.DecimalField(max_digits=8, decimal_places=0, verbose_name="Phone", blank=True, null=True)
    address = models.CharField(max_length=400, blank=True, null=True, verbose_name="Addresse",
                               help_text="Juste la Route (e.g: Rt Matar, Rt Sokra)")
    username = models.CharField(max_length=20, blank=True, verbose_name="GitHub username")
    birthday = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    # new = models.BooleanField(default=True)  # is new if now inscription on old session

    def is_new(self):
        today = date.today()
        if today.month < 9:
            first_day_on_session = date(today.year - 1, 9, 1)
        else:
            first_day_on_session = date(today.year, 9, 1)
        ins = self.inscription_set.filter(session__lt=first_day_on_session)
        return ins.count() == 0
    is_new.boolean = True

    def clean(self):
        # username is unique if not empty
        if self.username:
            m = Member.objects.filter(username__iexact=self.username)
            if self.id:
                m = m.exclude(id=self.id)
            if len(m):
                raise ValidationError("Username should be uniqe")

    def __str__(self):
        return "%s %s" % (self.name, self.family_name)


class Inscription(models.Model):
    ROLE = (
        ('a', 'President'),
        ('b', 'Vice President'),
        ('c', 'Secretary'),
        ('e', 'Tech Leader'),
        ('g', 'Treasurer'),
        ('k', 'Media Manager'),
        ('z', 'Admin'),
        ('', 'Member'),
    )
    UNIVERSITY_CHOICES = (
        ("FSS", "Faculté des Sciences de Sfax"),
        ("ENIS", "Ecole Nationale des Ingénieurs de Sfax"),
        ("ISIMS", "Institut Supérieur d'Informatique et de Multimédia de Sfax"),
        ("ENETCOM", "Ecole Nationale d'electronique et de télécommunications de Sfax"),
        ("FSEGS", "Faculté des Sciences Economiques et de Gestion de Sfax"),
        ("IPEIS", "Institut Préparatoire aux Etudes d'Ingénieurs de Sfax"),
        ("ISGIS", "Institut Supérieur de Gestion Industrielle de Sfax"),
        ("IPSAS", "Institut Polytechnique Privé des Sciences Avancées de Sfax"),
        ("ISETS", "Institut Supérieur des Etudes Technologiques de Sfax"),
        ("", "Autre..."),
    )
    EDUCATION_CHOICES = (
        ("LF", "Licence Fondamentale"),
        ("LA", "Licence Appliqué"),
        ("P", "Préparatoire"),
        ("ENG", "Ingéniorat"),
        ("MR", "Master de Recherche"),
        ("MP", "Master Professionnel"),
        ("PHD", "Doctorat"),
        ("", "Autre..."),
    )
    YEAR_CHOICES = (
        ('1', 1),
        ('2', 2),
        ('3', 3),
        ('', 'Autre...'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLE, default='', blank=True)
    session = models.DateField()  # auto_now_add=True
    inscription_num = models.DecimalField(verbose_name="Inscription Num",
                                          null=True, blank=True, max_digits=10,
                                          decimal_places=0,
                                          help_text="Seulement pour les étudiants du FSS pour le service culturel de la faculté.")
    university = models.CharField(verbose_name="Institution / University", choices=UNIVERSITY_CHOICES, default='FSS', max_length=7, blank=True)
    education = models.CharField(verbose_name="Cycle", choices=EDUCATION_CHOICES, default='LF', max_length=3, blank=True)
    year = models.CharField(verbose_name="Année", choices=YEAR_CHOICES, default='1', max_length=1, blank=True)
    confirmed = models.BooleanField(default=False)
    dreamspark_key = models.BooleanField(default=False)
    member_card = models.BooleanField(default=False)

    def is_current(self):
        _date = date.today()
        if _date.month < 9:
            _date = date(_date.year - 1, 9, 1)
        else:
            _date = date(_date.year, 9, 1)
        if (self.session > _date and
                self.session < date(_date.year + 1, _date.month, _date.day)):
                return True
        return False
    is_current.boolean = True

    def __str__(self):
        if self.session.month < 9:
            return "%d-%d" % (self.session.year - 1, self.session.year)
        else:
            return "%d-%d" % (self.session.year, self.session.year + 1)


class EventManager(models.Manager):

    def comming(self):
        return self.get_queryset().filter(Q(start_date__gte=date.today()) |
                                          Q(end_date__gte=date.today()))


class Event(models.Model):
    EVENT_TYPES = (
        ('con', 'conference'),
        ('cha', 'challenge'),
        ('tra', 'training'),
        ('tlk', 'talk'),
        ('unk', 'other'),
    )
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    event_type = models.CharField(max_length=3, choices=EVENT_TYPES)
    place = models.CharField(max_length=80, default='FSS')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_ours = models.BooleanField()

    objects = EventManager()

    def is_passed(self):
        if self.end_date is not None:
            end = self.end_date
        else:
            end = self.start_date
        return end < date.today()

    is_passed.boolean = True

    def __str__(self):
        return self.title


class EventLink(models.Model):
    title = models.CharField(max_length=40)
    link = models.URLField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# TODO: add Project model
