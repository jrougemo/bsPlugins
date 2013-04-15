from bsPlugins import *
from bbcflib.btrack import track
from bbcflib.bFlatMajor.common import *
from bbcflib.bFlatMajor.stream import concatenate
from bbcflib.bFlatMajor.figure import venn
from bbcflib import genrep
from itertools import combinations
import os

# nosetests --logging-filter=-tw2 test_VennDiagram.py

class VennDiagramForm(BaseForm):
    child = twd.HidingTableLayout()
    class SigMulti(Multi):
        label = "Files: "
        files = twf.FileField(label=' ',
            help_text='Select your track files',
            validator=twf.FileValidator(required=True))
    assembly = twf.SingleSelectField(label='Assembly: ',
        options=genrep.GenRep().assemblies_available(),
        validator=twc.Validator(required=True),
        help_text='Reference genome')
    submit = twf.SubmitButton(id="submit", value="Submit")


meta = {'version': "1.0.0",
        'author': "BBCF",
        'contact': "webmaster-bbcf@epfl.ch"}

in_parameters = [
        {'id':'files', 'type':'track', 'required':True, 'multiple':True},
        {'id':'assembly', 'type':'assembly'},
]
out_parameters = [{'id':'venn_diagram', 'type':'file'}]


class VennDiagramPlugin(BasePlugin):
    description = """

    """
    info = {
        'title': 'Venn Diagram',
        'description': description,
        'path': ['Graphics', 'Venn Diagram'],
        'output': VennDiagramForm,
        'in': in_parameters,
        'out': out_parameters,
        'meta': meta,
        }
    def __call__(self, **kw):
        assembly = genrep.Assembly(kw['assembly'])
        filenames = kw.get('files',[])
        if not isinstance(filenames,(list,tuple)): filenames = [filenames]
        tracks = [track(f) for f in filenames]
        track_names = [chr(i+65) for i in range(len(tracks))] # file name?, or 'A','B','C',...
        combn = [combinations(track_names,k) for k in range(1,len(tracks)+1)]
        combn = ['|'.join(sorted(y)) for x in combn for y in x]
        sets = dict(zip(combn,[0]*len(combn)))
        def _f(i): # hack
            return lambda x:track_names[i]
        for chrom in assembly.chrmeta:
            streams = [t.read(chrom) for t in tracks]
            streams = [duplicate(s,'chr','track_name') for s in streams]
            streams = [apply(s,'track_name',_f(i)) for i,s in enumerate(streams)]
            s = concatenate(streams, aggregate={'track_name':lambda x:'|'.join(x)})
            s = cobble(s)
            name_idx = s.fields.index('track_name')
            for x in s:
                subset = '|'.join(sorted(x[name_idx].split('|'))) # reorder letters
                sets[subset] += 1
        venn(sets)
        output = self.temporary_path(fname='venn_diagram.png')
        self.new_file(output, 'venn_diagram')
        return self.display_time()
