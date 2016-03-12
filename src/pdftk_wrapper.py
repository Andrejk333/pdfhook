import os
import subprocess
from tempfile import mkstemp

class PdftkError(Exception):
    pass

class PDFTKWrapper:

    def __init__(self, encoding='latin-1', tmp_path=None):
        self.encoding = encoding
        self.TEMP_FOLDER_PATH = tmp_path
        self._tmp_files = []

    def _coerce_to_file_path(self, path_or_file_or_bytes):
        """This converst file-like objects and `bytes` into
        existing files and returns a filepath
        if strings are passed in, it is assumed that they are existing
        files
        """
        if not isinstance(path_or_file_or_bytes, str):
            if isinstance(path_or_file_or_bytes, bytes):
                return self._write_tmp_file(
                    bytestring=path_or_file_or_bytes)
            else:
                return self._write_tmp_file(
                    file_obj=path_or_file_or_bytes)
        return path_or_file_or_bytes

    def _write_tmp_file(self, file_obj=None, bytestring=None):
        """Take a file-like object or a bytestring,
        create a temporary file and return a file path.
        file-like objects will be read and written to the tempfile
        bytes objects will be written directly to the tempfile
        """
        tmp_path = self.TEMP_FOLDER_PATH
        os_int, tmp_fp = mkstemp(dir=tmp_path)
        with open(tmp_fp, 'wb') as tmp_file:
            if file_obj:
                tmp_file.write(file_obj.read())
            elif bytestring:
                tmp_file.write(bytestring)
        self._tmp_files.append(tmp_fp)
        return tmp_fp

    def _clean_up_tmp_files(self):
        if not self._tmp_files:
            return
        for i in range(len(self._tmp_files)):
            path = self._tmp_files.pop()
            os.remove(path)

    def _get_file_contents(self, path, decode=False):
        """given a file path, return the contents of the file
        if decode is True, the contents will be decoded using the default
        encoding
        """
        bytestring = open(path, 'rb').read()
        if decode:
            return bytestring.decode(self.encoding)
        return bytestring

    def get_fdf(self, fp):
        """Given a path to a pdf form, this returns the decoded
        text of an output fdf file
        """
        fp = self._coerce_to_file_path(fp)
        tmp_outfile = self._write_tmp_file()
        self.run_command([fp, 'generate_fdf',
            'output', tmp_outfile])
        return self._get_file_contents(
            tmp_outfile, decode=True)

    def get_xfdf(self, fp):
        return None

    def get_data_fields(self, fp):
        return None

    def parse_fdf_fields(self, fdf_str):
        yield None

    def parse_xfdf_fields(self, xfdf_str):
        yield None

    def parse_data_fields(self, data_str):
        yield None

    def run_command(self, args):
        if args[0] != 'pdftk':
            args.insert(0, 'pdftk')
        process = subprocess.Popen(args,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            raise PdftkError(err.decode('utf-8'))
        return out.decode('utf-8')


