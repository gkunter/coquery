# -*- coding: utf-8 -*-
"""
sqlhelper.py is part of Coquery.

Copyright (c) 2016, 2017 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import unicode_literals

import logging

from .defines import SQL_SQLITE


def get_index_length(engine, table, column, coverage=0.95):
    """
    Return the index length that is required for the given coverage.

    If the current SQL engine is SQL_SQLITE, this method always returns
    None.

    Parameters
    ----------
    table, column : str
        The name of the table and the column, respectively

    coverage : float
        The coverage percentage that the index should cover. Default: 0.95

    Returns
    -------
    number : int
        The first character length that reaches the given coverage, or
        None if the coverage cannot be reached.
    """

    if engine.name == SQL_SQLITE:
        return None

    S = """
    SELECT len,
        COUNT(DISTINCT SUBSTR({column}, 1, len)) AS number,
        total,
        ROUND(COUNT(DISTINCT SUBSTR({column}, 1, len)) / total, 2) AS coverage
    FROM   {table}
    INNER JOIN (
        SELECT COUNT(DISTINCT {column}) total
        FROM   {table}
        WHERE  {column} != "") count_total
    INNER JOIN (
        SELECT @x := @x + 1 AS len
        FROM   {table}, (SELECT @x := 0) count_init
        LIMIT  32) count_inc
    GROUP BY len""".format(
        table=table, column=column)

    with engine.connect() as connection:
        results = connection.execute(S)

    max_c = None
    for x in results:
        if not max_c or x[3] > max_c[3]:
            max_c = x
        if x[3] >= coverage:
            print("{}.{}: index length {}".format(table, column, x[0]))
            logging.info("{}.{}: index length {}".format(table, column, x[0]))
            return int(x[0])
    if max_c:
        print("{}.{}: index length {}".format(table, column, max_c[0]))
        logging.info("{}.{}: index length {}".format(table, column, max_c[0]))
        return int(max_c[0])
    return None
