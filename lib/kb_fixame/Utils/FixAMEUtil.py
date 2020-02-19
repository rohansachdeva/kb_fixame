import errno
import json
import os
import subprocess
import sys
import time
import uuid
import psutil

from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.MetagenomeUtilsClient import MetagenomeUtils
from installed_clients.ReadsUtilsClient import ReadsUtils


def log(message, prefix_newline=False):
    """Logging function, provides a hook to suppress or redirect log messages."""
    print(('\n' if prefix_newline else '') + '{0:.2f}'.format(time.time()) + ': ' + str(message))


class FixAMEUtil:
    FIXAME_TOOLKIT_PATH = '/kb/deployment/bin/FixAME'

    def _validate_run_kb_fixame_params(self, params):
        """
        _validate_run_kb_fixame_params:
                validates params passed to run_kb_fixame method

        """
        log('Start validating run_kb_fixame params')

        # check for required parameters
        for p in ['assembly_ref', 'workspace_name', 'reads_list']:
            if p not in params:
                raise ValueError('"{}" parameter is required, but missing'.format(p))

    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _run_command(self, command):
        """
        _run_command: run command and print result
        """

        log('Start executing command:\n{}'.format(command))
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        output = pipe.communicate()[0]
        exitCode = pipe.returncode

        if (exitCode == 0):
            log('Executed command:\n{}\n'.format(command) +
                'Exit Code: {}\nOutput:\n{}'.format(exitCode, output))
        else:
            error_msg = 'Error running command:\n{}\n'.format(command)
            error_msg += 'Exit Code: {}\nOutput:\n{}'.format(exitCode, output)
            raise ValueError(error_msg)

    def _stage_reads_list_file(self, reads_list):
        """
        _stage_reads_list_file: download fastq file associated to reads to scratch area
                          and write result_file_path to file
        """

        log('Processing reads object list: {}'.format(reads_list))

        result_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(result_directory)
        result_file = os.path.join(result_directory, 'reads_list_file.txt')

        result_file_path = []

        reads = self.ru.download_reads({'read_libraries': reads_list,
                                        'interleaved': 'false'})['files']

        for read_obj in reads_list:
            files = reads[read_obj]['files']
            result_file_path.append(files['fwd'])
            if 'rev' in files and files['rev'] is not None:
                result_file_path.append(files['rev'])

        log('Saving reads file path(s) to: {}'.format(result_file))
        with open(result_file, 'w') as file_handler:
            for item in result_file_path:
                file_handler.write("{}\n".format(item))

        return result_file


    def _get_contig_file(self, assembly_ref):
        """
        _get_contig_file: get contif file from GenomeAssembly object
        """

        contig_file = self.au.get_assembly_as_fasta({'ref': assembly_ref}).get('path')

        sys.stdout.flush()
        contig_file = self.dfu.unpack_file({'file_path': contig_file})['file_path']

        return contig_file

    def _generate_command(self, params):
        """
        _generate_command: generate FixAME params
        """

        command = self.FIXAME_TOOLKIT_PATH + '/FixAME.py '

        command += '-i {} '.format(params.get('contig_file_path'))

        if params.get('reads_list_file'):
            reads_list_file_list = open(params.get('reads_list_file')).readlines()
            print('entry', reads_list_file_list)
            if len(reads_list_file_list) == 2:
                reads_list_file_list = [read_file.strip() for read_file in reads_list_file_list]
                forward_read, reverse_read = reads_list_file_list
                command += '-f {} '.format(forward_read)
                command += '-r {} '.format(reverse_read)

        if params.get('min_contig_length'):
            command += '-l {} '.format(params.get('min_contig_length'))

        command += '-o fixame_result.tsv '

        command += '-e fixame_report.tsv '

        command += '-m 1 '

        threads = psutil.cpu_count()
        command += '-t {} '.format(threads)

        log('Generated FixAME.py command: {}'.format(command))

        return command

    def _generate_output_file_list(self, result_directory):
        """
        _generate_output_file_list: zip result files and generate file_links for report
        """
        log('Start packing result files')
        output_files = list()

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
#        result_file = os.path.join(output_directory, 'fixame_result.tsv')
 #       report_file = os.path.join(output_directory, 'fixame_report.tsv')

        for root, dirs, files in os.walk(result_directory):
            print(root,dirs,files)
            for file in files:
                if file == 'fixame_result.tsv':
                    result_file = os.path.join(root, file)
                elif file == 'fixame_report.tsv':
                    report_file = os.path.join(root, file)


        output_files.append({'path': result_file,
                             'name': os.path.basename(result_file),
                             'label': os.path.basename(result_file),
                             'description': 'File(s) generated by FixAME App'})

        
        output_files.append({'path': report_file,
                             'name': os.path.basename(report_file),
                             'label': os.path.basename(report_file),
                             'description': 'Report generated by FixAME App'})

        return output_files

    def _generate_html_report(self, result_directory, assembly_ref):
        """
        _generate_html_report: generate html summary report
        """

        log('Start generating html report')
        html_report = list()

        output_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(output_directory)
        result_file_path = os.path.join(output_directory, 'report.html')

        Overview_Content = ''

        (input_contig_count,
        total_contig_length,
        type_local_assembly_error_bp,
        type_palindrome_length,
        type_direct_repeat_length,
        type_potential_circular_length,
        type_high_variability_bp,
        total_error_bp,
        percent_error_bp) = self._generate_overview_info(assembly_ref, result_directory)

        Overview_Content += '<p>Total Input Sequences: {}</p>'.format(input_contig_count)
        Overview_Content += '<p>Total Input Sequence Length: {}</p>'.format(total_contig_length)
        Overview_Content += '<p>Total Local Assembly Error Basepairs : {}</p>'.format(type_local_assembly_error_bp)
        Overview_Content += '<p>Total Palindromic Sequence Length: {}</p>'.format(type_palindrome_length)
        Overview_Content += '<p>Total Direct Repeat Sequence Length: {}</p>'.format(type_direct_repeat_length)
        Overview_Content += '<p>Total Potentially Circular Sequence Length: {}</p>'.format(type_potential_circular_length)
        Overview_Content += '<p>Total High Variability Basepairs: {}</p>'.format(type_high_variability_bp)
        Overview_Content += '<p>Total Error Basepairs: {}</p>'.format(total_error_bp)
        Overview_Content += '<p>Total Percent Error Basepairs: {}</p>'.format(percent_bp)

        with open(result_file_path, 'w') as result_file:
            with open(os.path.join(os.path.dirname(__file__), 'report_template.html'),
                      'r') as report_template_file:
                report_template = report_template_file.read()
                report_template = report_template.replace('<p>Overview_Content</p>',
                                                          Overview_Content)
                result_file.write(report_template)

        html_report.append({'path': result_file_path,
                            'name': os.path.basename(result_file_path),
                            'label': os.path.basename(result_file_path),
                            'description': 'HTML summary report for FixAMEApp'})
        return html_report

    def _generate_overview_info(self, assembly_ref, result_directory):
        assembly = self.dfu.get_objects({'object_refs': [assembly_ref]})['data'][0]
        input_contig_count = assembly.get('data').get('num_contigs')
        total_contig_length = 0

        for contig_id, contig in assembly.get('data').get('contigs').items():
            total_contig_length += int(contig.get('length'))

        report_dict = {}

        result_files = os.listdir(result_directory)

        for file_name in result_files:
            if file_name == 'fixame_report.tsv':
                report_list = open(file_name).readlines()

                for line in report_list[1:]:
                    line = line.strip().split('\t')
                    feature_error_type, count = line
                    report_dict[feature_error_type] = int(count)

                type_local_assembly_error_bp = report_dict['local_assembly_error']
                type_palindrome_length = report_dict['palindrome']
                type_direct_repeat_length = report_dict['direct_repeat']
                type_potential_circular_length = report_dict['potential_circular']
                type_high_variability_bp = report_dict['high_variability']

                total_error_bp = sum([type_local_assembly_error_bp,
                                             type_palindrome_length,
                                             type_direct_repeat_length])

                percent_error_bp = total_error_bp / total_contig_length * 100
                percent_error_bp = round(total_error_bp, 5)

                return (input_contig_count,
                        total_contig_length,
                        type_local_assembly_error_bp,
                        type_palindrome_length,
                        type_direct_repeat_length,
                        type_potential_circular_length,
                        type_high_variability_bp,
                        total_error_bp,
                        percent_error_bp)

    def _generate_report(self, result_directory, params):
        """
        generate_report: generate summary report

        """
        log('Generating report')

        output_files = self._generate_output_file_list(result_directory)

        output_html_files = self._generate_html_report(result_directory,
                                                       params.get('assembly_ref'))

        created_objects = []
        # created_objects.append({"ref": binned_contig_obj_ref,
        #                         "description": "BinnedContigs from MaxBin2"})

        report_params = {
            'message': '',
            'workspace_name': params.get('workspace_name'),
            'objects_created': created_objects,
            'file_links': output_files,
            'html_links': output_html_files,
            'direct_html_link_index': 0,
            'html_window_height': 266,
            'report_object_name': 'kb_fixame_report_' + str(uuid.uuid4())}

        kbase_report_client = KBaseReport(self.callback_url)
        output = kbase_report_client.create_extended_report(report_params)

        report_output = {'report_name': output['name'], 'report_ref': output['ref']}

        return report_output

    def __init__(self, config):
        self.callback_url = config['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.shock_url = config['shock-url']
        self.dfu = DataFileUtil(self.callback_url)
        self.ru = ReadsUtils(self.callback_url)
        self.au = AssemblyUtil(self.callback_url)
        self.mgu = MetagenomeUtils(self.callback_url)

    def run_kb_fixame(self, params):
        """
        run_kb_fixame: FixAME.py app

        required params:
            assembly_ref: Metagenome assembly object reference
            workspace_name: the name of the workspace it gets saved to.
            reads_list: list of reads object (PairedEndLibrary/SingleEndLibrary)
                        upon which FixAME will be run
        """
        log('--->\nrunning FixAMEUtil.run_kb_fixame\n' +
            'params:\n{}'.format(json.dumps(params, indent=1)))

        self._validate_run_kb_fixame_params(params)
        #        params['out_header'] = 'Bin'

        contig_file = self._get_contig_file(params.get('assembly_ref'))
        params['contig_file_path'] = contig_file

        reads_list_file = self._stage_reads_list_file(params.get('reads_list'))
        params['reads_list_file'] = reads_list_file

        result_directory = os.path.join(self.scratch, str(uuid.uuid4()))
        self._mkdir_p(result_directory)

        command = self._generate_command(params)

        cwd = os.getcwd()
        log('changing working dir to {}'.format(result_directory))
        os.chdir(result_directory)
        self._run_command(command)
        os.chdir(cwd)
        log('changing working dir to {}'.format(cwd))

        log('Saved result files to: {}'.format(result_directory))
        log('Generated files:\n{}'.format('\n'.join(os.listdir(result_directory))))

        #    generate_binned_contig_param = {
        #        'file_directory': result_directory,
        #        'assembly_ref': params.get('assembly_ref'),
        # #           'binned_contig_name': params.get('binned_contig_name'),
        #        'workspace_name': params.get('workspace_name')
        #    }
        #        binned_contig_obj_ref = self.mgu.file_to_binned_contigs(
        #                                   generate_binned_contig_param).get('binned_contig_obj_ref')

        #        reportVal = self._generate_report(binned_contig_obj_ref, result_directory, params)
        reportVal = self._generate_report(result_directory, params)
        returnVal = {
            'result_directory': result_directory
            # 'binned_contig_obj_ref': binned_contig_obj_ref
        }

        returnVal.update(reportVal)

        return returnVal
