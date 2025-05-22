from typing import Any, NamedTuple

import pandas as pd
import streamlit as st


class ComparisonTableData(NamedTuple):
    comparison_rows: list[Any]
    total_prev: pd.Series
    total_curr: pd.Series
    avg_prev: pd.Series
    avg_curr: pd.Series
    var_total_sales_copies: object
    var_total_sales_perc: object
    var_avg_sales_copies: object
    var_avg_sales_perc: object
    previous_year: int
    current_year: int


def config_columns_to_sales_boards(prev_year: int, curr_year: int) -> dict[str, Any]:
    """
    Configures the columns for the sales boards.
    Args:
        prev_year (int): The previous year.
        curr_year (int): The current year.
    Returns:
        dict[str, Any]: A dictionary containing the columns configuration.
    """

    prev = prev_year - 2000
    curr = curr_year - 2000

    columns_config = {
        #        'Year_prev': st.column_config.TextColumn(label='Year', width='small'),
        f'Issue_{prev}': st.column_config.TextColumn(label='Issue', width='small'),
        f'Date_{prev}': st.column_config.DateColumn(label='Date', width='small'),
        f'Supply_{prev}': st.column_config.NumberColumn(label='Supply', width='small'),
        f'Sales_{prev}': st.column_config.NumberColumn(label='Sales', width='small'),
        f'Unsolds_{prev}': st.column_config.NumberColumn(label='%Unsolds', width='small', format='percent', step=0.01),
        f'Outlet_{prev}': st.column_config.TextColumn(label='Outlet', width='small'),
        #        'Year_curr': st.column_config.TextColumn(label='Year', width='small'),
        f'Issue_{curr}': st.column_config.TextColumn(label='Issue', width='small'),
        f'Date_{curr}': st.column_config.DateColumn(label='Date', width='small'),
        f'Supply_{curr}': st.column_config.NumberColumn(label='Supply', width='small'),
        f'Sales_{curr}': st.column_config.NumberColumn(label='Sales', width='small'),
        f'Unsolds_{curr}': st.column_config.NumberColumn(label='%Unsolds', width='small', format='percent', step=0.01),
        f'Outlet_{curr}': st.column_config.TextColumn(label='Outlet', width='small'),
        'Copies_var': st.column_config.NumberColumn(label='Copies', width='small'),
        '%_var': st.column_config.NumberColumn(label='%', width='small', format='percent', step=0.01),
    }

    return columns_config


def highlight_negative(val):
    if pd.isna(val):
        return ''
    color = 'red' if val < 0 else 'white'
    return f'color: {color}'
