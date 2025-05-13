import decimal
from typing import List, Optional

from sqlalchemy import (
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


class Publication(Base, AuditMixin, PrimaryKeyMixin, ArrayColumnMixin):
    __tablename__ = 'ZPUBLIC'
    __table_args__ = (
        PrimaryKeyConstraint('ROWID', name='ZPUBLIC_ROWID'),
        Index('ZPUBLIC_ZPUB0', 'CODPUB_0', unique=True),
    )

    publication: Mapped[str] = mapped_column('CODPUB_0', Unicode(7, 'Latin1_General_BIN2'), server_default=text("''"))
    description: Mapped[str] = mapped_column('DESPUB_0', Unicode(30, 'Latin1_General_BIN2'), server_default=text("''"))
    shortDescription: Mapped[str] = mapped_column(
        'DESSHO_0', Unicode(10, 'Latin1_General_BIN2'), server_default=text("''")
    )
    sequence: Mapped[str] = mapped_column('PUBCOU_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    status: Mapped[int] = mapped_column('ZPUBSTA_0', TINYINT, server_default=text('((1))'))
    forecastStatus: Mapped[int] = mapped_column('PUBSTA_0', TINYINT, server_default=text('((1))'))
    category: Mapped[str] = mapped_column('TCLCOD_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    lineProduct: Mapped[str] = mapped_column('CFGLIN_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BPSNUM',
        property_name='supplier',
        count=2,
        column_type=Unicode(15, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    suppliers: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    publisher: Mapped[str] = mapped_column('BPSEDI_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''"))
    referenceSupplier: Mapped[str] = mapped_column(
        'BPSREF_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''")
    )

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='TSICOD',
        property_name='statisticalCode',
        count=5,
        column_type=Unicode(20, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    statisticalGroup: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='CRY',
        property_name='country',
        count=2,
        column_type=Unicode(3, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    countries: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    language: Mapped[str] = mapped_column('LAN_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    periodicity: Mapped[str] = mapped_column('CODPER_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''"))
    periodNumber: Mapped[int] = mapped_column('PERNUM_0', TINYINT, server_default=text('((1))'))
    shippingMethod: Mapped[str] = mapped_column(
        'SHIWAY_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''")
    )
    percentageIncrease: Mapped[decimal.Decimal] = mapped_column(
        'PERMAJ_0', Numeric(10, 3), server_default=text('((0))')
    )
    distributionForm: Mapped[int] = mapped_column('FORDIS_0', TINYINT, server_default=text('((1))'))
    company: Mapped[str] = mapped_column('CPY_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PURBASPRI',
        property_name='purchaseBasePrice',
        count=7,
        column_type=Numeric(18, 5),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    purchaseBasePrices: Mapped[List[Optional[decimal.Decimal]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BASPRI',
        property_name='defaultPrice',
        count=7,
        column_type=Numeric(14, 3),
        python_type=decimal.Decimal,
        server_default=text('((0))'),
    )

    defaultPrices: Mapped[List[Optional[decimal.Decimal]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    purchasePrice: Mapped[decimal.Decimal] = mapped_column('PURPRI_0', Numeric(14, 3), server_default=text('((0))'))
    defaultPrice: Mapped[decimal.Decimal] = mapped_column('PRICE_0', Numeric(14, 3), server_default=text('((0))'))
    taxLevel: Mapped[str] = mapped_column('VACITM_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    supplierDiscount: Mapped[decimal.Decimal] = mapped_column('DSCBPS_0', Numeric(10, 3), server_default=text('((0))'))
    agentDiscount: Mapped[decimal.Decimal] = mapped_column('DSCAGE_0', Numeric(10, 3), server_default=text('((0))'))
    vaspDiscount: Mapped[decimal.Decimal] = mapped_column('DSCVSP_0', Numeric(10, 3), server_default=text('((0))'))
    newsOnBoardDiscount: Mapped[decimal.Decimal] = mapped_column(
        'DSCNOB_0', Numeric(10, 3), server_default=text('((0))')
    )
    returnPercentage: Mapped[decimal.Decimal] = mapped_column('PERDEV_0', Numeric(10, 3), server_default=text('((0))'))
    vaspCode: Mapped[str] = mapped_column('PUBVSP_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='PUBDAY',
        property_name='publicationDay',
        count=7,
        column_type=TINYINT,
        python_type=int,
        server_default=text('((1))'),
    )

    distributionDays: Mapped[List[Optional[int]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    holiday: Mapped[int] = mapped_column('HOLIDAY_0', TINYINT, server_default=text('((1))'))
    isbn: Mapped[str] = mapped_column('ISBN_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='EANCOD',
        property_name='eanCode',
        count=7,
        column_type=Unicode(20, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    eanCodes: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    iva: Mapped[decimal.Decimal] = mapped_column('CDIVVD_0', Numeric(16, 7), server_default=text('((0))'))
    sendVasp: Mapped[int] = mapped_column('FLGENV_0', TINYINT, server_default=text('((1))'))
    product: Mapped[int] = mapped_column('ITMFLG_0', TINYINT, server_default=text('((1))'))
    tariffCode: Mapped[str] = mapped_column('CUSREF_0', Unicode(12, 'Latin1_General_BIN2'), server_default=text("''"))
    timeToSell: Mapped[int] = mapped_column('TIMSAL_0', Integer, server_default=text('((0))'))
    leftovers: Mapped[str] = mapped_column('CODSCR_0', Unicode(20, 'Latin1_General_BIN2'), server_default=text("''"))
    quantityToStorage: Mapped[int] = mapped_column('QTYARM_0', Integer, server_default=text('((0))'))
    quantityToEditor: Mapped[int] = mapped_column('QTYEDI_0', Integer, server_default=text('((0))'))
    specialQuantity: Mapped[int] = mapped_column('QTYESP_0', Integer, server_default=text('((0))'))
    exportQuantity: Mapped[int] = mapped_column('QTYEXP_0', Integer, server_default=text('((0))'))
    isVaspDistribution: Mapped[int] = mapped_column('DISTVSP_0', TINYINT, server_default=text('((1))'))
    expeditionMode: Mapped[str] = mapped_column('MDL_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    referenceCode: Mapped[str] = mapped_column(
        'REFEDI_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''")
    )
    extension: Mapped[str] = mapped_column('EXTEDI_0', Unicode(2, 'Latin1_General_BIN2'), server_default=text("''"))

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BIPAD',
        property_name='bipad',
        count=7,
        column_type=Unicode(15, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    bipads: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BIPEXT',
        property_name='bipadExtension',
        count=7,
        column_type=Unicode(3, 'Latin1_General_BIN2'),
        python_type=str,
        server_default=text("''"),
    )

    bipadExtensions: Mapped[List[Optional[str]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='BIPDEF',
        property_name='defaultBipad',
        count=7,
        column_type=TINYINT,
        python_type=int,
        server_default=text('((1))'),
    )

    defaultBipads: Mapped[List[Optional[int]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    _properties, _columns = ArrayColumnMixin.create_array_property(
        db_column_prefix='POLO',
        property_name='polo',
        count=10,
        column_type=TINYINT,
        python_type=int,
        server_default=text('((1))'),
    )

    polos: Mapped[List[Optional[int]]] = _properties

    for _attr_name, _mapped_column in _columns.items():
        locals()[_attr_name] = _mapped_column

    del _attr_name, _mapped_column, _properties, _columns

    manager: Mapped[str] = mapped_column('PUBGES_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''"))
    analyst: Mapped[str] = mapped_column('PUBANA_0', Unicode(15, 'Latin1_General_BIN2'), server_default=text("''"))
    billable: Mapped[int] = mapped_column('FATFLG_0', TINYINT, server_default=text('((1))'))
    notes: Mapped[str] = mapped_column('NOTAS_0', Unicode(250, 'Latin1_General_BIN2'), server_default=text("''"))
    package: Mapped[str] = mapped_column('PCK_0', Unicode(5, 'Latin1_General_BIN2'), server_default=text("''"))
    capacity: Mapped[int] = mapped_column('PCKCAP_0', SmallInteger, server_default=text('((0))'))
    returnEDI: Mapped[int] = mapped_column('RETFLG_0', TINYINT, server_default=text('((1))'))
    sendToNewsOnBoard: Mapped[int] = mapped_column('DLVFLG_0', TINYINT, server_default=text('((1))'))
    debitDistribution: Mapped[decimal.Decimal] = mapped_column('DEBDIS_0', Numeric(14, 3), server_default=text('((0))'))
    debitReturn: Mapped[decimal.Decimal] = mapped_column('DEBDEV_0', Numeric(14, 3), server_default=text('((0))'))
