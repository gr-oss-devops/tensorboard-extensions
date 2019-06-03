import argparse
import os
import signal
import sys
import threading

from tensorboard import program
from tensorboard import version
from tensorboard.backend.event_processing import event_file_inspector as efi
from tensorboard.plugins import base_plugin

from .application import gr_tensorboard_wsgi
from .logging import _logger

try:
  from absl import flags as absl_flags
  from absl.flags import argparse_flags
except ImportError:
  # Fall back to argparse with no absl flags integration.
  absl_flags = None
  argparse_flags = argparse

class GRTensorBoard(object):
  def __init__(self, program_tensorboard):
    self.tensorboard_instance = program_tensorboard
  
  def configure(self, argv=('',), **kwargs):
    self.tensorboard_instance.configure(argv, **kwargs)
  
  def main(self, ignored_argv=('',)):
    self._install_signal_handler(signal.SIGTERM, "SIGTERM")
    if self.tensorboard_instance.flags.inspect:
      _logger.log_message_info('Not bringing up GRTensorBoard, but inspecting event files.')
      event_file = os.path.expanduser(self.tensorboard_instance.flags.event_file)
      efi.inspect(self.tensorboard_instance.flags.logdir, event_file, self.tensorboard_instance.flags.tag)
      return 0
    try:
      server = self._make_server()
      sys.stderr.write('GRTensorBoard %s at %s (Press CTRL+C to quit)\n' %
                       (version.VERSION, server.get_url()))
      sys.stderr.flush()
      server.serve_forever()
      return 0
    except program.TensorBoardServerException as e:
      _logger.log_message_info("Error: " + e.msg)
      sys.stderr.write('ERROR: %s\n' % e.msg)
      sys.stderr.flush()
      return -1

  def launch(self):
    """Python API for launching GRTensorBoard.

    This method is the same as main() except it launches TensorBoard in
    a separate permanent thread. The configure() method must be called
    first.

    Returns:
      The URL of the GRTensorBoard web server.

    :rtype: str
    """
    # Make it easy to run TensorBoard inside other programs, e.g. Colab.
    server = self._make_server()
    thread = threading.Thread(target=server.serve_forever, name='GRTensorBoard')
    thread.daemon = True
    thread.start()
    return server.get_url()

  def _register_info(self, server):
    self.tensorboard_instance._register_info(server)
  
  def _install_signal_handler(self, signal_number, signal_name):
    self.tensorboard_instance._install_signal_handler(signal_number, signal_name)
  
  def _make_server(self):
    app = gr_tensorboard_wsgi(self.tensorboard_instance.flags, self.tensorboard_instance.plugin_loaders, self.tensorboard_instance.assets_zip_provider)
    return self.tensorboard_instance.server_class(app, self.tensorboard_instance.flags)
  

