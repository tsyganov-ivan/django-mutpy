from django.core.management.base import BaseCommand

from mutpy.controller import MutationController, FirstOrderMutator
from mutpy.utils import ModulesLoader
from mutpy.views import TextView
from mutpy import operators


class Command(BaseCommand):
    help = 'Run mutation testing'

    def hack_django_for_mutate(self):
        import django.urls.resolvers as r

        def set_cb(self, value):
            self._cb = value

        def callback(self):
            import importlib
            module = importlib.import_module(self._cb.__module__)
            return module.__dict__.get(self._cb.__name__)

        r.RegexURLPattern.callback = property(callback, set_cb)

    def __init__(self, *args, **kwargs):
        self.hack_django_for_mutate()
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('--target', type=str, nargs='+')
        parser.add_argument('--unit-test', type=str, nargs='+')
        parser.add_argument('--experimental-operators')

    def handle(self, *args, **options):
        operators_set = operators.standard_operators
        if options['experimental_operators']:
            operators_set |= operators.experimental_operators

        controller = MutationController(
            target_loader=ModulesLoader(options['target'], None),
            test_loader=ModulesLoader(options['unit_test'], None),
            views=[TextView(colored_output=False, show_mutants=True)],
            mutant_generator=FirstOrderMutator(operators_set)
        )
        controller.run()
