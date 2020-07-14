import unittest

import numpy as np

import openmdao.api as om
from openmdao.utils.units import convert_units
from openmdao.utils.assert_utils import assert_near_equal


class TestVectorMagnitudeCompNx3(unittest.TestCase):

    def setUp(self):
        self.nn = 5

        self.p = om.Problem()

        ivc = om.IndepVarComp()
        ivc.add_output(name='a', shape=(self.nn, 3))

        self.p.model.add_subsystem(name='ivc',
                                   subsys=ivc,
                                   promotes_outputs=['a'])

        self.p.model.add_subsystem(name='vec_mag_comp',
                                   subsys=om.VectorMagnitudeComp(vec_size=self.nn))

        self.p.model.connect('a', 'vec_mag_comp.a')

        self.p.setup()

        self.p['a'] = 1.0 + np.random.rand(self.nn, 3)

        self.p.run_model()

    def test_results(self):

        for i in range(self.nn):
            a_i = self.p['a'][i, :]
            mag_i = self.p['vec_mag_comp.a_mag'][i]
            expected_i = np.sqrt(np.dot(a_i, a_i))

            np.testing.assert_almost_equal(mag_i, expected_i)

    def test_partials(self):
        np.set_printoptions(linewidth=1024)
        cpd = self.p.check_partials(compact_print=False, method='fd', step=1.0E-9, out_stream=None)

        for comp in cpd:
            for (var, wrt) in cpd[comp]:
                np.testing.assert_almost_equal(actual=cpd[comp][var, wrt]['J_fwd'],
                                               desired=cpd[comp][var, wrt]['J_fd'],
                                               decimal=5)


class TestVectorMagnitudeCompNx4(unittest.TestCase):
    def setUp(self):
        self.nn = 100

        self.p = om.Problem()

        ivc = om.IndepVarComp()
        ivc.add_output(name='a', shape=(self.nn, 4))

        self.p.model.add_subsystem(name='ivc',
                                   subsys=ivc,
                                   promotes_outputs=['a'])

        self.p.model.add_subsystem(name='vec_mag_comp',
                                   subsys=om.VectorMagnitudeComp(vec_size=self.nn, length=4))

        self.p.model.connect('a', 'vec_mag_comp.a')

        self.p.setup()

        self.p['a'] = 1.0 + np.random.rand(self.nn, 4)

        self.p.run_model()

    def test_results(self):

        for i in range(self.nn):
            a_i = self.p['a'][i, :]
            mag_i = self.p['vec_mag_comp.a_mag'][i]
            expected_i = np.sqrt(np.dot(a_i, a_i))

            np.testing.assert_almost_equal(mag_i, expected_i)

    def test_partials(self):
        np.set_printoptions(linewidth=1024)
        cpd = self.p.check_partials(compact_print=False, method='fd', step=1.0E-9, out_stream=None)

        for comp in cpd:
            for (var, wrt) in cpd[comp]:
                np.testing.assert_almost_equal(actual=cpd[comp][var, wrt]['J_fwd'],
                                               desired=cpd[comp][var, wrt]['J_fd'],
                                               decimal=6)


class TestUnits(unittest.TestCase):

    def setUp(self):
        self.nn = 5

        self.p = om.Problem()

        ivc = om.IndepVarComp()
        ivc.add_output(name='a', shape=(self.nn, 3), units='m')

        self.p.model.add_subsystem(name='ivc',
                                   subsys=ivc,
                                   promotes_outputs=['a'])

        self.p.model.add_subsystem(name='vec_mag_comp',
                                   subsys=om.VectorMagnitudeComp(vec_size=self.nn, units='m'))

        self.p.model.connect('a', 'vec_mag_comp.a')

        self.p.setup()

        self.p['a'] = 1.0 + np.random.rand(self.nn, 3)

        self.p.run_model()

    def test_results(self):

        for i in range(self.nn):
            a_i = self.p['a'][i, :]
            c_i = self.p.get_val('vec_mag_comp.a_mag', units='ft')[i]
            expected_i = np.sqrt(np.dot(a_i, a_i)) / 0.3048

            np.testing.assert_almost_equal(c_i, expected_i)

    def test_partials(self):
        np.set_printoptions(linewidth=1024)
        cpd = self.p.check_partials(compact_print=True, out_stream=None)

        for comp in cpd:
            for (var, wrt) in cpd[comp]:
                np.testing.assert_almost_equal(actual=cpd[comp][var, wrt]['J_fwd'],
                                               desired=cpd[comp][var, wrt]['J_fd'],
                                               decimal=6)


class TestMultipleUnits(unittest.TestCase):

    def setUp(self):
        self.nn = 5


        ivc = om.IndepVarComp()
        ivc.add_output(name='a', shape=(self.nn, 3), units='m')
        ivc.add_output(name='b', shape=(2*self.nn, 2), units='ft')

        vmc = om.VectorMagnitudeComp(vec_size=self.nn, units='m')
        vmc.add_magnitude('b_mag', 'b', vec_size=2*self.nn, length=2, units='ft')

        model = om.Group()

        model.add_subsystem('ivc', subsys=ivc, promotes_outputs=['a', 'b'])
        model.add_subsystem('vmc', subsys=vmc)

        model.connect('a', 'vmc.a')
        model.connect('b', 'vmc.b')

        p = self.p = om.Problem(model)
        p.setup()

        p['a'] = 1.0 + np.random.rand(self.nn, 3)
        p['b'] = 1.0 + np.random.rand(2*self.nn, 2)

        p.run_model()

    def test_results(self):

        for i in range(self.nn):
            a_i = self.p['a'][i, :]
            am_i = self.p.get_val('vmc.a_mag', units='ft')[i]
            expected_i = np.sqrt(np.dot(a_i, a_i)) / 0.3048

            np.testing.assert_almost_equal(am_i, expected_i)

            b_i = self.p['b'][i, :]
            bm_i = self.p.get_val('vmc.b_mag', units='m')[i]
            expected_i = np.sqrt(np.dot(a_i, a_i)) * 0.3048

    def test_partials(self):
        np.set_printoptions(linewidth=1024)
        cpd = self.p.check_partials(compact_print=True, out_stream=None)

        for comp in cpd:
            for (var, wrt) in cpd[comp]:
                np.testing.assert_almost_equal(actual=cpd[comp][var, wrt]['J_fwd'],
                                               desired=cpd[comp][var, wrt]['J_fd'],
                                               decimal=6)


class TestMultipleErrors(unittest.TestCase):

    def test_duplicate_outputs(self):
        vmc = om.VectorMagnitudeComp()
        vmc.add_magnitude('a_mag', 'aa')

        model = om.Group()
        model.add_subsystem('vmc', vmc)

        p = om.Problem(model)

        with self.assertRaises(NameError) as ctx:
            p.setup()

        self.assertEqual(str(ctx.exception), "VectorMagnitudeComp (vmc): "
                         "Multiple definition of output 'a_mag'.")

    def test_input_as_output(self):
        vmc = om.VectorMagnitudeComp()
        vmc.add_magnitude('a', 'aa')

        model = om.Group()
        model.add_subsystem('vmc', vmc)

        p = om.Problem(model)

        with self.assertRaises(NameError) as ctx:
            p.setup()

        self.assertEqual(str(ctx.exception), "VectorMagnitudeComp (vmc): 'a' specified as"
                         " an output, but it has already been defined as an input.")

    def test_output_as_input(self):
        vmc = om.VectorMagnitudeComp()
        vmc.add_magnitude('aa', 'a_mag')

        model = om.Group()
        model.add_subsystem('vmc', vmc)

        p = om.Problem(model)

        with self.assertRaises(NameError) as ctx:
            p.setup()

        self.assertEqual(str(ctx.exception), "VectorMagnitudeComp (vmc): 'a_mag' specified as"
                         " an input, but it has already been defined as an output.")

    def test_vec_size_mismatch(self):
        vmc = om.VectorMagnitudeComp()
        vmc.add_magnitude('a_mag2', 'a', vec_size=10)

        model = om.Group()
        model.add_subsystem('vmc', vmc)

        p = om.Problem(model)

        with self.assertRaises(ValueError) as ctx:
            p.setup()

        self.assertEqual(str(ctx.exception), "VectorMagnitudeComp (vmc): "
                         "Conflicting vec_size=10 specified for input 'a', "
                         "which has already been defined with vec_size=1.")

    def test_length_mismatch(self):
        vmc = om.VectorMagnitudeComp()
        vmc.add_magnitude('a_mag2', 'a', length=5)

        model = om.Group()
        model.add_subsystem('vmc', vmc)

        p = om.Problem(model)

        with self.assertRaises(ValueError) as ctx:
            p.setup()

        self.assertEqual(str(ctx.exception), "VectorMagnitudeComp (vmc): "
                         "Conflicting length=5 specified for input 'a', "
                         "which has already been defined with length=1.")

    def test_units_mismatch(self):
        vmc = om.VectorMagnitudeComp()
        vmc.add_magnitude('a_mag2', 'a', units='ft')

        model = om.Group()
        model.add_subsystem('vmc', vmc)

        p = om.Problem(model)

        with self.assertRaises(ValueError) as ctx:
            p.setup()

        self.assertEqual(str(ctx.exception), "VectorMagnitudeComp (vmc): "
                         "Conflicting units specified for input 'a', 'None' and 'ft'.")


class TestFeature(unittest.TestCase):

    def test(self):
        """
        A simple example to compute the magnitude of 3-vectors at at 100 points simultaneously.
        """
        import numpy as np
        import openmdao.api as om

        n = 100

        p = om.Problem()

        ivc = om.IndepVarComp()
        ivc.add_output(name='pos', shape=(n, 3), units='m')

        p.model.add_subsystem(name='ivc',
                              subsys=ivc,
                              promotes_outputs=['pos'])

        dp_comp = om.VectorMagnitudeComp(vec_size=n, length=3, in_name='r', mag_name='r_mag',
                                         units='km')

        p.model.add_subsystem(name='vec_mag_comp', subsys=dp_comp)

        p.model.connect('pos', 'vec_mag_comp.r')

        p.setup()

        p['pos'] = 1.0 + np.random.rand(n, 3)

        p.run_model()

        # Verify the results against numpy.dot in a for loop.
        for i in range(n):
            a_i = p['pos'][i, :]
            expected_i = np.sqrt(np.dot(a_i, a_i)) / 1000.0
            assert_near_equal(p.get_val('vec_mag_comp.r_mag')[i], expected_i)


if __name__ == '__main__':
    unittest.main()
