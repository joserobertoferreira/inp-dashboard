import datetime
import decimal
from typing import List, Optional

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    Numeric,
    PrimaryKeyConstraint,
    SmallInteger,
    Unicode,
    text,
)
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.orm import Mapped, mapped_column

from core.base import Base
from core.generics_mixins import ArrayColumnMixin
from core.mixins import AuditMixin, PrimaryKeyMixin


class Users(Base, AuditMixin, PrimaryKeyMixin, ArrayColumnMixin):
    __tablename__ = 'AUTILIS'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='AUTILIS_ROWID'),
        Index('AUTILIS_CODUSR', 'USR_0', unique=True),
        Index('AUTILIS_LOGIN', 'LOGIN_0'),
    )

    name: Mapped[str] = mapped_column('NOMUSR_0', Unicode(30, 'Latin1_General_BIN2'), server_default=text("''"))
    username: Mapped[str] = mapped_column('USR_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    login: Mapped[str] = mapped_column('LOGIN_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''"))
    password: Mapped[str] = mapped_column('ZPWDHASH_0', Unicode(128, 'Latin1_General_BIN2'), server_default=text("''"))
    email: Mapped[str] = mapped_column('ADDEML_0', Unicode(80, 'Latin1_General_BIN2'))

    PWDBI_0: Mapped[str] = mapped_column(Unicode(24, 'Latin1_General_BIN2'))
    PASSE_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    DATCONN_0: Mapped[datetime.datetime] = mapped_column(DateTime, server_default='1753-01-01')
    DECTIME_0: Mapped[int] = mapped_column(Integer)
    DIFIMP_0: Mapped[int] = mapped_column(TINYINT)
    ENAFLG_0: Mapped[int] = mapped_column(TINYINT)
    FAX_0: Mapped[str] = mapped_column(Unicode(40, 'Latin1_General_BIN2'))
    BPRNUM_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    NBRCON_0: Mapped[int] = mapped_column(SmallInteger)
    PASSDAT_0: Mapped[datetime.datetime] = mapped_column(DateTime)
    TELEP_0: Mapped[str] = mapped_column(Unicode(40, 'Latin1_General_BIN2'))
    TIMCONN_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='CHEF',
        property_name='chef',
        count=20,
        column_type=Unicode(35, 'Latin1_General_BIN2'),  # type: ignore
        python_type=str,
        server_default=text("''"),
    )

    chefs: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    CODMET_0: Mapped[str] = mapped_column(Unicode(4, 'Latin1_General_BIN2'))
    PRFMEN_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    PRFFCT_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    USRBI_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    NBFNC_0: Mapped[int] = mapped_column(SmallInteger)

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FNCCOD',
        property_name='function_code',
        count=8,
        column_type=Unicode(12, 'Latin1_General_BIN2'),  # type: ignore
        python_type=str,
        server_default=text("''"),
    )

    function_codes: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='FNCPAR',
        property_name='function_parameter',
        count=8,
        column_type=Unicode(10, 'Latin1_General_BIN2'),  # type: ignore
        python_type=str,
        server_default=text("''"),
    )

    function_parameters: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    ALLACS_0: Mapped[int] = mapped_column(TINYINT)
    USREXT_0: Mapped[int] = mapped_column(TINYINT)
    CHGDAT_0: Mapped[int] = mapped_column(TINYINT)
    REPNUM_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    USRCONNECT_0: Mapped[int] = mapped_column(TINYINT)
    USRCONXTD_0: Mapped[int] = mapped_column(TINYINT)
    CODADRDFT_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    CODRIBDFT_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PRTDEF',
        property_name='printer_definition',
        count=10,
        column_type=Unicode(10, 'Latin1_General_BIN2'),  # type: ignore
        python_type=str,
        server_default=text("''"),
    )

    printers_definition: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    ACSUSR_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    NEWPAS_0: Mapped[str] = mapped_column(Unicode(24, 'Latin1_General_BIN2'))
    BPAADD_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    BIDNUM_0: Mapped[str] = mapped_column(Unicode(30, 'Latin1_General_BIN2'))
    RPCREP_0: Mapped[int] = mapped_column(SmallInteger)
    USRPRT_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    TIT_0: Mapped[str] = mapped_column(Unicode(250, 'Latin1_General_BIN2'))
    ADDNAM_0: Mapped[str] = mapped_column(Unicode(250, 'Latin1_General_BIN2'))
    PRFXTD_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
    ARCPRF_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    FNC_0: Mapped[int] = mapped_column(TINYINT)
    FLGPASPRV_0: Mapped[int] = mapped_column(TINYINT)
    STA_0: Mapped[int] = mapped_column(TINYINT)
    WITHOUTLDAP_0: Mapped[int] = mapped_column(TINYINT)
    MSNSTR_0: Mapped[datetime.datetime] = mapped_column(DateTime)
    MSNEND_0: Mapped[datetime.datetime] = mapped_column(DateTime)
    MNA_0: Mapped[int] = mapped_column(TINYINT)
    KILRAT_0: Mapped[decimal.Decimal] = mapped_column(Numeric(14, 3))
    CUR_0: Mapped[str] = mapped_column(Unicode(3, 'Latin1_General_BIN2'))
    FULTIM_0: Mapped[int] = mapped_column(TINYINT)
    NBDAY_0: Mapped[int] = mapped_column(SmallInteger)

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='AUSDAY',
        property_name='ausday',
        count=7,
        column_type=TINYINT,  # type: ignore
        python_type=int,
        server_default=text('((0))'),
    )

    ausdays: Mapped[List[Optional[int]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='ARVHOU',
        property_name='arrival_time',
        count=7,
        column_type=Unicode(6, 'Latin1_General_BIN2'),  # type: ignore
        python_type=str,
        server_default=text("''"),
    )

    arrival_times: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='DPEHOU',
        property_name='departure_time',
        count=7,
        column_type=Unicode(6, 'Latin1_General_BIN2'),  # type: ignore
        python_type=str,
        server_default=text("''"),
    )

    departure_times: Mapped[List[Optional[str]]] = _properties  # type: ignore

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    ESCSTRDAT_0: Mapped[datetime.datetime] = mapped_column(DateTime)
    NBRESC_0: Mapped[int] = mapped_column(SmallInteger)
    HDKREP_0: Mapped[int] = mapped_column(TINYINT)
    AUZDSCDEM_0: Mapped[int] = mapped_column(TINYINT)
    ACCCOD_0: Mapped[str] = mapped_column(Unicode(10, 'Latin1_General_BIN2'))
    WRH_0: Mapped[str] = mapped_column(Unicode(5, 'Latin1_General_BIN2'))
