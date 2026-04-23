from django.contrib import auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User, PermissionsMixin, UserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps.registry import apps
import shortuuid


def generate_short_uuid():
    """生成短UUID"""
    return shortuuid.ShortUUID().random(length=22)
# Create your models here.
class UserStatusChoices(models.IntegerChoices):
    # 用户状态
    #已激活
    ACTIVE = 1
    #未激活
    UNACTIVE = 2
    #锁定
    LOCKED = 3

class UserRoleChoices(models.IntegerChoices):
    """用户角色选择"""
    STUDENT = 1, '学生'
    COACH = 2, '教练'
    ADMIN = 3, '管理员'

class OJUserManager(BaseUserManager):
    use_in_migrations = True

    def _validate_superuser_fields(self, extra_fields):
        """验证超级用户字段的合法性"""
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

    def _create_user_object(self, username, realname, email, password, **extra_fields):

        if not realname:
            raise ValueError("必须设置真实姓名")
        email = self.normalize_email(email)
        # Lookup the real model class from the global app registry so this
        # manager method can be used in migrations. This is fine because
        # managers are by definition working on the real model.
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, realname=realname, email=email, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, username, realname, email, password, **extra_fields):
        """
        创建用户
        Create and save a user with the given username, email, and password.
        """
        user = self._create_user_object(username,realname, email, password, **extra_fields)
        user.save(using=self._db)
        return user

    async def _acreate_user(self, username, realname, email, password, **extra_fields):
        """See _create_user()"""
        user = self._create_user_object(username, realname, email, password, **extra_fields)
        await user.asave(using=self._db)
        return user

    def create_user(self, username, realname, email=None, password=None, **extra_fields):
        #创建普通用户
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, realname, email, password, **extra_fields)

    create_user.alters_data = True

    async def acreate_user(self, username, realname, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return await self._acreate_user(username, realname, email, password, **extra_fields)

    acreate_user.alters_data = True

    def create_superuser(self, username, realname, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        self._validate_superuser_fields(extra_fields)

        return self._create_user(username, realname, email, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(
        self, username, realname, email=None, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        self._validate_superuser_fields(extra_fields)

        return await self._acreate_user(username, realname, email, password, **extra_fields)

    acreate_superuser.alters_data = True

    def with_perm(
        self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth.get_backends()
            if len(backends) == 1:
                backend = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


#重写User
class OJUser(AbstractBaseUser, PermissionsMixin):
    """
    自定义的User模型
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """

    username_validator = UnicodeUsernameValidator()

    uid = models.CharField(
        primary_key=True,
        max_length=22,
        default=generate_short_uuid,
        editable=False,
        verbose_name='UID'
    )

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    realname = models.CharField(
        _("realname"),
        max_length=150,
        unique=False,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
    )
    email = models.EmailField(_("email address"),unique=True)
    telephone = models.CharField(
        max_length=20,
        unique=True,
        validators=[UnicodeUsernameValidator()]
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    status = models.IntegerField(choices=UserStatusChoices, default=UserStatusChoices.UNACTIVE)
    role = models.IntegerField(
        choices=UserRoleChoices,
        default=UserRoleChoices.STUDENT,
        verbose_name='用户角色'
    )
    avatar = models.URLField(
        blank=True,
        default='',
        verbose_name='头像URL'
    )
    bio = models.TextField(
        blank=True,
        default='',
        verbose_name='个人简介'
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)

    objects = OJUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "realname"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = False

    def __str__(self):
      return self.username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_realname(self):
        return self.realname

    def get_username(self):
        """Return the short name for the user."""
        return self.username

    def is_student(self):
        """判断是否为学生"""
        return self.role == UserRoleChoices.STUDENT

    def is_coach(self):
        """判断是否为教练"""
        return self.role == UserRoleChoices.COACH

    def is_admin_user(self):
        """判断是否为管理员"""
        return self.role == UserRoleChoices.ADMIN or self.is_superuser


class Class(models.Model):
    """班级模型"""
    name = models.CharField(max_length=100, unique=True, verbose_name='班级名称')
    coach = models.ForeignKey(
        OJUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='managed_classes',
        verbose_name='班主任/教练'
    )
    description = models.TextField(blank=True, default='', verbose_name='班级描述')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'ojauth_class'
        verbose_name = '班级'
        verbose_name_plural = '班级'
    
    def __str__(self):
        return self.name


class ClassMember(models.Model):
    """班级成员关系"""
    class_obj = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='班级'
    )
    user = models.ForeignKey(
        OJUser,
        on_delete=models.CASCADE,
        related_name='classes',
        verbose_name='学生'
    )
    join_time = models.DateTimeField(auto_now_add=True, verbose_name='加入时间')
    
    class Meta:
        db_table = 'ojauth_class_member'
        verbose_name = '班级成员'
        verbose_name_plural = '班级成员'
        unique_together = ['class_obj', 'user']
    
    def __str__(self):
        return f"{self.user.username} in {self.class_obj}"
