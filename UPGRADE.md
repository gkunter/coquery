There are several changes in Pandas and Numpy that the current code base
of Coquery may not have implemented fully yet. Here's a list:

- np.float is deprecated; float should be used instead
- Pandas doesn't have a np property for Numpy any more; use np directly
- pd.read_csv() has replaced argument 'error_bad_lines=bool' by 'on_bad_lines="warn"
- SQLAlchemy requires that all execution strings are wrapped with sqlalchemy.text()
- DataFrame.append() doesn't exist anymore; use pd.concat([...], ignore_index=True) instead
- use pd.concat(df, pd.DataFrame([row]), axis=0, ignore_index=True) to add a row
