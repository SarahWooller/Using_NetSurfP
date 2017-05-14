import re
import pandas as pd

def convert_to_csv(directory,filename):
    """takes the output from NetSurfP and spits out the relevant csv saved to the directory/root_of_filename.csv"""
    with open(directory+filename,'r') as file:
        f = file.read()
    F = f.split('\n')
    column = re.compile('.*Column.*')
    columns = [i.split(':')[1] for i in F if column.match(i)] 
    datum = re.compile('[A-Z]\s+[A-Z]\s+\S.*') 
    # typical example 'E T  sp_P04637-2_P53_HUMAN   329    0.274  38.045   0.973   0.011   0.918   0.071'
    data = [ i.split() for i in F if datum.match(i)]
    df = pd.DataFrame(data)
    df.columns = columns
    to_dot = r'.*\.'
    new_name = re.match(to_dot,filename).group()+'csv'
    df.to_csv(directory+new_name)

def find_mutants(df, mutation_list):
    """for a given list of mutations returns just those rows of a pandas dataframe that correspond to the mutations
    In addition provides a description of the problem for any mutations that do not have a corresponding line"""
    df[' Amino acid number']=pd.to_numeric(df[' Amino acid number'])
    matched = []
    unmatched = {}
    name_set = set(df[' Sequence name'])
    mut_exp = r'.*_[A-Z](\d+)[A-Z]'
    for mut in mutation_list:
        pos = int(re.match(mut_exp, mut).group(1))
        if mut in name_set:
            df1=df.loc[df[' Sequence name']==mut]
            if pos in df1[' Amino acid number']:
                df2 = df1.loc[df1[' Amino acid number']==pos]
                matched.append(df2.ix[df2.index[0]])
            else:
                unmatched[mut]='amino acids too short'

        else:
            unmatched[mut]='mutation not found'
    return (pd.concat(matched),unmatched)