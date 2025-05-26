import os
from string import Template
from nipype.interfaces.matlab import MatlabCommand
from nipype.interfaces.base import TraitedSpec, BaseInterface, BaseInterfaceInputSpec, File

'''
This script is used to define a number of digital signal processing functions to be created and passed into the pipeline
as functions within a node. These require MATLAB or Octave. These can be substituted with corresponding scipy functions.
'''

"""
The following code creates a node for nipype to pass outputs from the previous node into. 
This is used to bandpass filter and detrend regressors.
"""

class GenericBpfDtInputSpec(BaseInterfaceInputSpec):
    """ Configures the input interface for bandpass filtering and detrending """
    in_file = File(exists=True, mandatory=True, desc='Input file to be processed')
    out_file = File(mandatory=True, desc='Name of the output file')

class GenericBpfDtOutputSpec(TraitedSpec):
    """ Configures the output interface for nipype. """
    out_file = File(exists=True, desc='Path to the processed output file')

class GenericBpfDt(BaseInterface):
    """
    Generic Nipype interface for bandpass filtering and detrending a file.
    """
    input_spec = GenericBpfDtInputSpec
    output_spec = GenericBpfDtOutputSpec

    def _run_interface(self, runtime):
        """
        Creates a dictionary to insert infile and outfile name,
        runs the matlab commands specified and saves the runtime variables.
        """
        d = dict(in_file=self.inputs.in_file,
                 out_file=self.inputs.out_file)
        # MATLAB code template
        script = Template(
            """oned = load('$in_file'); 
                bpf = bandpass(oned, [0.01 0.08]);
                bpfdt = detrend(bpf, 2);
                save('$out_file', 'bpfdt', '-ascii');
                exit;
                """
        ).substitute(d)

        mlab = MatlabCommand(script=script, mfile=True)
        result = mlab.run()

        return result.runtime

    def _list_outputs(self):
        """Gets appropriate runtime variable and stores as output"""
        outputs = self._outputs().get()
        outputs['out_file'] = os.path.abspath(self.inputs.out_file)
        return outputs


'''
The following code concatenates the outputs from the previous steps into a unified regressor matrix using matlab
'''


class concatInputSpec(BaseInterfaceInputSpec):
    in_file_a = File(exists=True, mandatory=True)
    in_file_b = File(exists=True, mandatory=True)
    out_file = File('regmodel.1D', usedefault=True)


class concatOutputSpec(TraitedSpec):
    out_file = File(exists=True)


class ConcatModel(BaseInterface):
    input_spec = concatInputSpec
    output_spec = concatOutputSpec

    def _run_interface(self, runtime):
        a = dict(in_file_a=self.inputs.in_file_a,
                 in_file_b=self.inputs.in_file_b,
                 out_file=self.inputs.out_file)
        # this is your MATLAB code template
        conscript = Template("""moco = load('$in_file_a');
        csf = load('$in_file_b');
        regmodel = horzcat(csf, moco);
        save('$out_file', 'regmodel', '-ascii');
        exit;""").substitute(a)

        z = MatlabCommand(script=conscript, mfile=True)
        res = z.run()

        return res.runtime

    def _list_outputs(self):
        outputs = self._outputs().get()
        outputs['out_file'] = os.path.abspath('regmodel.1D')
        return outputs


# this is a quick function to tell python how to find the right file from the segmentation function
pickindex = lambda x, i: x[i]
