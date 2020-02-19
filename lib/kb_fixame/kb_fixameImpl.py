# -*- coding: utf-8 -*-
#BEGIN_HEADER
import os
import json

from kb_fixame.Utils.FixAMEUtil import FixAMEUtil
#END_HEADER


class kb_fixame:
    '''
    Module Name:
    kb_fixame

    Module Description:
    A KBase module: kb_fixame
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/rohansachdeva/kb_fixame.git"
    GIT_COMMIT_HASH = "7f05631c3bd75fd9a02f1688344aa4ce634169ad"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.config = config
        self.config['SDK_CALLBACK_URL'] = os.environ['SDK_CALLBACK_URL']
        self.config['KB_AUTH_TOKEN'] = os.environ['KB_AUTH_TOKEN']
        #END_CONSTRUCTOR
        pass


    def run_kb_fixame(self, ctx, params):
        """
        :param params: instance of type "FixAMEInputParams" (required params:
           assembly_ref: Genome assembly object reference #       
           binned_contig_name: BinnedContig object name and output file
           header workspace_name: the name of the workspace it gets saved to.
           reads_list: list of reads object
           (PairedEndLibrary/SingleEndLibrary) upon which FixAME will be run
           optional params: #        thread: number of threads; default 1 #  
           reassembly: specify this option if you want to reassemble the
           bins. note that at least one reads file needs to be designated. # 
           prob_threshold: minimum probability for EM algorithm; default 0.8
           #        markerset: choose between 107 marker genes by default or
           40 marker genes #        min_contig_length: minimum contig length;
           default 1000 #        plotmarker: specify this option if you want
           to plot the markers in each contig #        ref:
           http://downloads.jbei.org/data/microbial_communities/MaxBin/README.
           txt) -> structure: parameter "assembly_ref" of type "obj_ref" (An
           X/Y/Z style reference), parameter "workspace_name" of String,
           parameter "reads_list" of list of type "obj_ref" (An X/Y/Z style
           reference), parameter "min_contig_length" of Long
        :returns: instance of type "FixAMEResult" (result_folder: folder path
           that holds all files generated by run_kb_fixame report_name:
           report name generated by KBaseReport report_ref: report reference
           generated by KBaseReport) -> structure: parameter
           "result_directory" of String, parameter "report_name" of String,
           parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN run_kb_fixame
        print('--->\nRunning kb_fixame.run_kb_fixame\nparams:')
        print(json.dumps(params, indent=1))

        for key, value in params.items():
            if isinstance(value, str):
                params[key] = value.strip()

        fixame_runner = FixAMEUtil(self.config)
        returnVal = fixame_runner.run_kb_fixame(params)
        #END run_kb_fixame

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method run_kb_fixame return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
