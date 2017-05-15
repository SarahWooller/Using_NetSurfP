import re
import pandas as pd
import json
import re
import sys
import subprocess
import os

class Mut:
    
    def __init__(self,mut):
        
        self.mut = mut
        self.messages = {'ok':(True,'no problems encountered' ),
                         'no ENST':(False,'no ENSTs correspond to this Uniprot code'),
                         'too short':(False, "none of the corresponding codes were long enough to encorporate this "+
                                      "mutation"),
                         'wrong wild type': (False, "whilst at least one of the corresponding codes was long enough to"+
                                             "encorporate this mutation the AA did not correspond to the wild type given")
                        
                        }

    
        parts = mut.split('_')
        self.name = parts[0]
        self.mutation = parts[1]
        self.wild = self.mutation[0]
        self.change = self.mutation[-1]
        self.pos = int(self.mutation[1:-1])
        
        self.valid,self.ENSTs = self.get_ENSTs()
        self.valid,self.ENST,self.wild_code = self.get_code()
        self.mutant_code = self.mutate_code()
        
        
    def get_ENSTs(self):
        i=self.name
        if i[:4]=='ENST':
            return [i]
        elif i in set(ENST_Uniprot['UniProtKB/Swiss-Prot ID']):
            Uni = 'UniProtKB/Swiss-Prot ID'
        elif i in set(ENST_Uniprot['UniProtKB/TrEMBL ID']):
            Uni = 'UniProtKB/TrEMBL ID'
        else:
            return (self.messages['no ENST'],'')
        return (self.messages['ok'],list(ENST_Uniprot[ENST_Uniprot[Uni]==i].index))
    
    def get_code(self):
        length_ok = False
        pos_ok = False
        
        codes = [ENST_codes.get(m,'') for m in self.ENSTs]
        C = len(codes)
        
        for i in range(C):
            if len(codes[i])>=self.pos:
                length_ok = True
                if codes[i][self.pos-1]==self.wild:
                    pos_ok = True
                    return (self.messages['ok'],self.ENSTs[i],codes[i])
        if not length_ok:
            return (self.messages['too short'],'','')
        else:
            return (self.messages['wrong wild type'],'','')
    
    def mutate_code(self):
        return self.wild_code[:self.pos-1]+self.change+self.wild_code[self.pos:]
        
    def for_printing(self):
        return ('>{0}_{1}'.format(self.ENST,self.mut),Split(self.mutant_code,61))

def refine_questions():
    temp = os.listdir('./temp_questions')
    pattern = re.compile('questions(\d+)\.*fsa')
    return [l for l in temp if pattern.match(l)]


def clean_directories():
    subprocess.Popen(['rm','-rf', os.path.abspath('./temp_questions/')])
    subprocess.Popen(['mkdir', 'temp_questions'])
    subprocess.Popen(['rm','-rf', os.path.abspath('./temp_answers/')])
    subprocess.Popen(['mkdir', 'temp_answers'])

def do_netsurfp(file_number):

    for j in range(file_number):
        input_file = 'temp_questions/questions{}.fsa'.format(j)
        output_file = 'temp_answers/answers{}.rsa'.format(j)
        p = subprocess.Popen(['netsurfp', '-i',input_file, '-o', output_file])
        p.communicate()
        print('{} completed'.format(j))

def Split(string,n):
	"""Split a string into lines of length n with \n in between them"""
	N =len(string)//n
	return '\n'.join([string[i*n:(i+1)*n] for i in range(N)]+[string[N*n:]])

def make_NetSurfP_query():
    muts = get_query()
    mutations =[Mut(l) for l in muts]
    validity = dict(zip([m.name for m in mutations],[m.valid for m in mutations]))
    for_printing = [m.for_printing() for m in mutations]
    temp_lists = dont_exceed_max(10000,for_printing)
    make_questions('./temp_questions/','questions', temp_lists)
    mutations_listed=[[i[0] for i in j] for j in temp_lists]
    fine, too_short,wrong_wild = split_validity(validity)
    
    query = {'fine':fine,
            'too short': too_short,
            'wrong wild': wrong_wild,
            'mutations for netsurfp': mutations_listed}
    
    with open('./temp_answers/query.json','w') as file:
        json.dump(query,file)

def make_questions(pathname, filename, temp_lists):q 
    for t in range(len(temp_lists)):
        name = pathname+filename+str(t)+'.fsa'
        with open(name,'w') as file:
            file.write('')
        with open(name,'a') as file:
            for i in temp_lists[t]:
                a,b = i
                file.write(a+'\n')
                file.write(b+'\n')

def split_validity(validity):
    too_short=[]
    wrong_wild=[]
    fine = []
    for v in validity:
        a,b = validity[v]
        if a:
            fine.append(v)
        elif b=='none of the corresponding codes were long enough to encorporate this mutation':
            too_short.append(v)
        else:
            wrong_wild.append(v)
    return (fine, too_short,wrong_wild)

def dont_exceed_max(Max,code_list):
    """I need to ensure that NetSurfP is not overwhelmed - so I split the queries to ensure that each is less than Max
	I will use Max = 100000"""
    C = len(code_list)
    temp_list=[]
    for_inclusion=[]
    limit = 0
    for i in range(C):
        a,b = code_list[i]
        B = len(b)
        if limit+B<Max:
            for_inclusion.append(code_list[i])
            limit+=B
        else:
            temp_list.append(for_inclusion)
            limit=B
            for_inclusion=[code_list[i]]
    temp_list.append(for_inclusion)
    return temp_list

def get_query():
    print('To use this program you need to supply a file with a list of mutation codes\n',
         'These codes should be in the form of identifier_M244V where here\n',
         'M is the wild type 244 is the position and V is the mutant amino acid\n',
         'Your file should contain one mutation code per line and no other information\n')
    query_file = input('please type the full path of the file that contains your mutation codes here')
    try:
        with open(query_file,'r') as file:
            tmp = file.readlines()
        return [t.strip('\n') for t in tmp]
    except FileNotFoundError:
        print('file not found, quit and try again')
        return []


def get_ENST_codes():
	with open(os.path.abspath('./data/ENST_codes.json', 'r') as file:
		return json.load(file)

def get_ENST_Uniprot():     
    return pd.DataFrame.from_csv(os.path.abspath('./data/ENST_Uniprot.csv'))


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


def main():
    ENST_codes = get_ENST_codes()
    print('got ENST codes')
    ENST_Uniprot = get_ENST_Uniprot()
    print('got ENST Uniprot')
    clean_directories()
    print('directories cleaned')
    file_number = make_NetSurfP_query()
    print('queries made')
    do_netsurfp(file_number)
    print('netsurfp completed')


if __name__== "__main__":
	main()
