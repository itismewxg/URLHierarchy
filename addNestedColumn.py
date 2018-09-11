from pyspark.sql.functions import *
from pyspark.sql.types import *

def add_field_in_dataframe(nfield, df, dt): 
    fields = nfield.split(".")
    print fields
    n = len(fields)
    addField = fields[0]
    if n == 1:
        return df.withColumn(addField, lit(None).cast(dt))

    nestedField = ".".join(fields[:-1])
    sfields = df.select(nestedField).schema[fields[-2]].dataType.names
    print sfields
    ac = col(nestedField)
    if n == 2:
        nc = struct(*( [ac[c].alias(c) for c in sfields] + [lit(None).cast(dt).alias(fields[-1])]))
    else:
        nc = struct(*( [ac[c].alias(c) for c in sfields] + [lit(None).cast(dt).alias(fields[-1])])).alias(fields[-2])
    print nc
    n = n - 1

    while n > 1: 
        print "n: ",n
        fields = fields[:-1]
        print "fields: ", fields
        nestedField = ".".join(fields[:-1])
        print "nestedField: ", nestedField
        sfields = df.select(nestedField).schema[fields[-2]].dataType.names
        print fields[-1]
        print "sfields: ", sfields
        sfields = [s for s in sfields if s != fields[-1]]
        print "sfields: ", sfields
        ac = col(".".join(fields[:-1]))
        if n > 2: 
            print fields[-2]
            nc = struct(*( [ac[c].alias(c) for c in sfields] + [nc])).alias(fields[-2])
        else:
            nc = struct(*( [ac[c].alias(c) for c in sfields] + [nc]))
        n = n - 1
    return df.withColumn(addField, nc)
