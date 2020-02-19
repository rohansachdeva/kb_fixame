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
        workspace_name: the name of the workspace it gets saved to.
        reads_list: list of reads object (PairedEndLibrary/SingleEndLibrary) upon which FixAME will be run

        optional params:
        min_contig_length: minimum contig length; default 1000

        ref: Placeholder for FixAME ref
    */
    typedef structure {
        obj_ref assembly_ref;
        string workspace_name;
        list<obj_ref> reads_list;

        int min_contig_length;
    } FixAMEInputParams;

    /*
        result_folder: folder path that holds all files generated by run_kb_fixame
        report_name: report name generated by KBaseReport
        report_ref: report reference generated by KBaseReport
    */
    typedef structure{
        string result_directory;
        string report_name;
        string report_ref;
    }FixAMEResult;

    funcdef run_kb_fixame(FixAMEInputParams params)
        returns (FixAMEResult returnVal) authentication required;

};