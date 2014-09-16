#!/usr/bin/env python
# coding=utf-8
import json
import sys


def main():
    filename = sys.argv[1]
    notebook = json.load(open(filename))
    cells = notebook['worksheets'][0]['cells']

    for cell in cells:
        if cell['cell_type'] == 'markdown':
            # Easy
            print ''.join(cell['source'])
        elif cell['cell_type'] == 'code':
            # Can't use ``` or any shortcuts as markdown fails for some code
            print "{% highlight python %}"

            print "In [{}]: {}".format(
                cell['prompt_number'],
                '\n'.join(cell['input'])
            )

            try:
                assert all(o['output_type'] in ('stream', 'pyout', 'pyerr')
                           for o in cell['outputs'])
            except AssertionError:
                import IPython; IPython.embed()

            for output in cell['outputs']:
                if output['output_type'] in ('stream', 'pyout'):
                    print "Out [{}]: {}".format(
                        cell['prompt_number'],
                        ''.join(output['text'])
                    )
                elif output['output_type'] == 'pyerr':
                    print output['traceback']
                else:
                    print output
                    import IPython; IPython.embed()

            print "{% endhighlight %}"
        print ""

if __name__ == '__main__':
    main()
