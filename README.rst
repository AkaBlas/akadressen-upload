``akadressen-upload``
=====================

Small helper script to upload new AkaDressen files to internal section of the `AkaBlas <https://akablas.de>`_ Homepage.
It requires Python 3.12+.

Setting in up
-------------

Create a file ``.env`` with the following contents:

.. code-block::

    FTP_host=<host address of the ftp server>
    FTP_USERNAME=<username>
    FTP_PASSWORD=<password>
    SOURCE_PATH=<path to the folder containing the files to upload>
    TARGET_PATH=<path to the folder on the ftp server where the files should be uploaded>

Usage
-----

Run the script with the following command:

.. code-block:: shell

    python main.py

How It Works
------------

The script does the following:

1. Rename all files starting with ``latest_``. The new prefix is the modification date of the file.
2. Upload all files to the ftp server. The files will be prefixed with ``latest_``.
