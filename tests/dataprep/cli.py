import unittest

from docopt import DocoptExit

from dataprep.__main__ import parse_command_line
from dataprep.prepconfig import PrepParam, PrepConfig


class CliTest(unittest.TestCase):
    def test_parse_command_line_00010(self):
        argv = ['str', '--no-spaces', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_from_args_3x0xx(self):
        argv = ['str', '--no-spaces', '--no-unicode', 'nosplit']
        with self.assertRaises(DocoptExit) as context:
            parse_command_line(argv)

    def test_parse_command_line_x20xx(self):
        argv = ['str', '--no-spaces', '--no-str', '--no-com', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_xx00x(self):
        argv = ['str', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_xx0x1(self):
        argv = ['str', '--no-spaces', '--no-case','nosplit']
        with self.assertRaises(DocoptExit) as context:
            parse_command_line(argv)

    def test_parse_command_line_00111(self):
        argv = ['str', '--no-spaces', '--no-case', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_3x1xx(self):
        argv = ['str', '--no-spaces', '--no-case', '--no-unicode', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 3,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_x11xx(self):
        argv = ['str', '--no-spaces', '--no-case', '--no-str', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 1,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_x21xx(self):
        argv = ['str', '--no-spaces', '--no-case', '--no-str', '--no-com', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_x31xx(self):
        argv = ['str', '--no-spaces', '--no-case', '--no-com', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 3,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_012xx(self):
        argv = ['str', '--no-spaces', '--no-case', 'basic+numbers']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 2,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_014xx(self):
        argv = ['str', '--no-spaces', '--no-case', 'bpe', '5k']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 4,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_015xx(self):
        argv = ['str', '--no-spaces', '--no-case', 'bpe', '1k']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 5,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_xx6xx(self):
        argv = ['str', '--no-spaces', '--no-case', 'bpe', '10k']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 6,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_xx8xx(self):
        argv = ['str', '--no-spaces', '--no-case', 'chars']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 8,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_xx10x(self):
        argv = ['str', '--no-case', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 0,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_xx1x1(self):
        argv = ['str', '--no-spaces', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_path(self):
        argv = ['--path', '/path/to/dataset', '--no-spaces', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_path_short(self):
        argv = ['-p', '/path/to/dataset', '--no-spaces', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_output(self):
        argv = ['--path', '/path/to/dataset', '--output-path', '/path/to/output', '--no-spaces', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_output_short(self):
        argv = ['--path', '/path/to/dataset', '-o', '/path/to/output', '--no-spaces', 'nosplit']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 0,
            PrepParam.COM_STR: 0,
            PrepParam.SPLIT: 0,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 0
        })
        self.assertEqual(expected, actual[0])

    def test_parse_command_line_text_with_output(self):
        argv = ['str', '-o', '/path/to/output', '--no-spaces', 'nosplit']
        with self.assertRaises(DocoptExit) as context:
            parse_command_line(argv)

    def test_parse_command_line_all_short_config_options(self):
        argv = ['str', '-0lSCU', 'basic']
        actual = parse_command_line(argv)
        expected = PrepConfig({
            PrepParam.EN_ONLY: 3,
            PrepParam.COM_STR: 2,
            PrepParam.SPLIT: 1,
            PrepParam.TABS_NEWLINES: 1,
            PrepParam.CAPS: 1
        })
        self.assertEqual(expected, actual[0])


if __name__ == '__main__':
    unittest.main()
