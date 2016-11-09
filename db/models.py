from datetime import date
from django.utils import timezone

from django.db import models
from django.db.models.query_utils import Q
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.


class Member(models.Model):
    name = models.CharField(max_length=40, verbose_name="Prénom / Name")
    family_name = models.CharField(max_length=40,
                                   verbose_name="Nom / Family Name")
    email = models.EmailField(unique=True, verbose_name="E-mail",
                              db_index=True)
    phone = models.DecimalField(max_digits=8, decimal_places=0,
                                verbose_name="Phone", blank=True, null=True)
    address = models.CharField(
        max_length=400, blank=True, null=True, verbose_name="Addresse",
        help_text="Juste la Route (e.g: Rt Matar, Rt Sokra)")
    username = models.CharField(max_length=20, blank=True,
                                verbose_name="GitHub username")
    birthday = models.DateField(blank=True, null=True,
                                verbose_name="Date de naissance")

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
            if m.exists():
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
        ("ISIMS",
         "Institut Supérieur d'Informatique et de Multimédia de Sfax"),
        ("ENETCOM",
         "Ecole Nationale d'electronique et de télécommunications de Sfax"),
        ("FSEGS", "Faculté des Sciences Economiques et de Gestion de Sfax"),
        ("IPEIS", "Institut Préparatoire aux Etudes d'Ingénieurs de Sfax"),
        ("ISGIS", "Institut Supérieur de Gestion Industrielle de Sfax"),
        ("IPSAS",
         "Institut Polytechnique Privé des Sciences Avancées de Sfax"),
        ("ISETS", "Institut Supérieur des Etudes Technologiques de Sfax"),
        ("IIT", "Institut International de Technologie Sfax"),
    )
    EDUCATION_CHOICES = (
        ("LF", "Licence Fondamentale"),
        ("LA", "Licence Appliqué"),
        ("P", "Préparatoire"),
        ("ENG", "Ingéniorat"),
        ("MR", "Master de Recherche"),
        ("MP", "Master Professionnel"),
        ("PHD", "Doctorat"),
    )
    YEAR_CHOICES = (
        ('1', 1),
        ('2', 2),
        ('3', 3),
    )
    SESSIONS = (
        ('2014-2015', '2014-2015'),
        ('2015-2016', '2015-2016'),
        ('2016-2017', '2016-2017'),
    )
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    role = models.CharField(max_length=1, choices=ROLE, default='', blank=True)
    date = models.DateField(auto_now_add=True)
    session = models.CharField(choices=SESSIONS, default=SESSIONS[-1][1],
                               max_length=9)
    inscription_num = models.DecimalField(
        verbose_name="Inscription Num", null=True, blank=True, max_digits=10,
        decimal_places=0, help_text="Seulement pour les étudiants du FSS pour "
        "le service culturel de la faculté.")
    university = models.CharField(verbose_name="Institution / University",
                                  choices=UNIVERSITY_CHOICES,
                                  max_length=7, blank=True)
    education = models.CharField(verbose_name="Diplome courant",
                                 choices=EDUCATION_CHOICES,
                                 max_length=3, blank=True)
    year = models.CharField(verbose_name="Année", choices=YEAR_CHOICES,
                            max_length=1, blank=True)
    confirmed = models.BooleanField(default=False)
    dreamspark_key = models.BooleanField(default=False)
    member_card = models.BooleanField(default=False)

    class Meta:
        unique_together = ("member", "session")

    def is_current(self):
        return self.get_session_display() == self.current_session()
    is_current.boolean = True

    @staticmethod
    def current_session():
        today = date.today()
        if today.month < 9:
            return "%d-%d" % (today.year - 1, today.year)
        else:
            return "%d-%d" % (today.year, today.year + 1)

    def __str__(self):
        return self.get_session_display()


@receiver(post_save, sender=Inscription)
def inscription_confirmation(sender, instance, created, raw, using,
                             update_fields, **kwargs):
    if created and instance.member:
        from .email import send_mails
        send_mails([instance.member.email],
                   "Welcome to Fss Open Tech Club!",
                   """Welcome Fss Open Tech Club member,

- You need to create an account at github.com to access Fss OTC projects.
- Please confirm your email address and your GitHub account by sending your
GitHub username to fssotc@gmail.com.

Sincerely,

---
Open Tech Club - Faculty of Sciences of Sfax

Phone: (+216) 28 204 299
Website: mtcfss.azurewebsites.net
Facebook: fb.me/fssotc
E-mail: fssotc@gmail.com
GitHub: github.com/fssotc""")

    # if "dreamspark_key" in update_fields:
    # FIXME: email dreamspark key


class EventManager(models.Manager):

    def comming(self):
        return self.get_queryset().filter(Q(start__gte=date.today()) |
                                          Q(end__gte=date.today()))


class Event(models.Model):
    EVENT_TYPES = (
        ('con', 'conference'),
        ('cha', 'challenge'),
        ('tra', 'training'),
        ('tlk', 'talk'),
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    event_type = models.CharField(max_length=3, choices=EVENT_TYPES,
                                  blank=True)
    place = models.CharField(max_length=80,
                             default='Faculty of Sciences of Sfax, Amphi A9')
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    is_ours = models.BooleanField()
    price = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Price (-5 for members)")

    objects = EventManager()

    def is_passed(self):
        if self.end is not None:
            end = self.end
        else:
            end = self.start
        return end < timezone.now()

    is_passed.boolean = True

    def __str__(self):
        return self.title


class EventLink(models.Model):
    title = models.CharField(max_length=40)
    link = models.URLField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
