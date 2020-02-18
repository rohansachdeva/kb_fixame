/*
A KBase module: kb_fixame
*/

module kb_fixame {

    /* A boolean - 0 for false, 1 for true.
        @range (0, 1)
    */
    typedef int boolean;

    /* An X/Y/Z style reference
    */
    typedef string obj_ref;

    /*  
        required params:
        assembly_ref: Genome assembly object reference
#        binned_contig_name: BinnedContig object name and output file header
        workspace_name: the name of the workspace it gets saved to.
        reads_list: list of reads object (PairedEndLibrary/SingleEndLibrary) upon which FixAME will be run

        optional params:
#        thread: number of threads; default 1
#        reassembly: specify this option if you want to reassemble the bins.
                    note that at least one reads file needs to be designated.
#        prob_threshold: minimum probability for EM algorithm; default 0.8
#        markerset: choose between 107 marker genes by default or 40 marker genes
#        min_contig_length: minimum contig length; default 1000
#        plotmarker: specify this option if you want to plot the markers in each contig

#        ref: http://downloads.jbei.org/data/microbial_communities/MaxBin/README.txt
    */
    typedef structure {
        obj_ref assembly_ref;
        string workspace_name;
        list<obj_ref> reads_list;

        int min_contig_length;
    } FixAMEInputParams;

    /*
        result_folder: folder path that holds all files generated by run_fixame
        report_name: report name generated by KBaseReport
        report_ref: report reference generated by KBaseReport
    */
    typedef structure{
        string result_directory;
        string report_name;
        string report_ref;
    }FixAMEResult;

    funcdef run_fixame(FixAMEInputParams params)
        returns (FixAMEResult returnVal) authentication required;

};