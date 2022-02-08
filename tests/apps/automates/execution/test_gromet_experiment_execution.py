from automates.apps.automates.execute_driver import execute_gromet_experiment_json


def test_execute_sir_simple_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "gromet-fn", "source": '{"name": "SimpleSIR"}'},
        "start": 0,
        "end": 120.0,
        "step": 30.0,
        "domain_parameter": "P:sir.in.dt",
        "parameters": {
            "P:sir.in.beta": 0.5,
            "P:sir.in.S": 100000,
            "P:sir.in.I": 1,
            "P:sir.in.R": 0,
            "P:sir.in.gamma": 0.07,
        },
        "outputs": [
            "P:sir.out.S",
            "P:sir.out.I",
            "P:sir.out.R",
        ],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "result": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "P:sir.out.I": [
                    13.899850001499987,
                    193.17455602717965,
                    2678.622276802565,
                    35981.04345749553,
                    273225.5469052609,
                ],
                "P:sir.out.R": [
                    2.1,
                    31.289685003149977,
                    436.9562526602273,
                    6062.063033945615,
                    81622.25429468622,
                ],
                "P:sir.out.S": [
                    99985.0001499985,
                    99776.53575896967,
                    96885.4214705372,
                    57957.893508558845,
                    -254846.80119994713,
                ],
            },
        },
        "status": "success",
        "code": 200,
    }

    assert expected == result


def test_execute_chime_sir_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "gromet-fn", "source": '{"name": "CHIME-SIR"}'},
        "start": 0,
        "end": 120.0,
        "step": 30,
        "domain_parameter": "J:main.n_days",
        "parameters": {
            "J:main.i_day": 17.0,
            "J:main.N_p": 3,
            "J:main.infections_days": 14.0,
            "J:main.relative_contact_rate": 0.05,
            "J:main.s_n": 200,
            "J:main.i_n": 1,
            "J:main.r_n": 1,
        },
        "outputs": ["P:main.out.S", "P:main.out.I", "P:main.out.E", "P:main.out.R"],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "result": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "P:main.out.E": [0.0, 0.0, 0.0, 0.0, 0.0],
                "P:main.out.I": [
                    0.0,
                    0.8933233135653156,
                    0.7806198884453974,
                    0.6712711762750359,
                    0.5693715755370689,
                ],
                "P:main.out.R": [
                    0.0,
                    2.965680650912271,
                    4.763081925816063,
                    6.3215644582752715,
                    7.652866183157096,
                ],
                "P:main.out.S": [
                    0.0,
                    198.14099603552242,
                    196.45629818573855,
                    195.00716436544968,
                    193.77776224130582,
                ],
            },
        },
        "status": "success",
        "code": 200,
    }

    assert result == expected


def test_execute_chime_sviivr_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "gromet-fn", "source": '{"name": "CHIME_SVIIvR"}'},
        "start": 0,
        "end": 120.0,
        "step": 30,
        "domain_parameter": "J:main.n_days",
        "parameters": {
            "J:main.i_day": 17.0,
            "J:main.N_p": 20,
            "J:main.infectious_days_unvaccinated": 14,
            "J:main.infectious_days_vaccinated": 10,
            "J:main.vaccination_rate": 0.02,
            "J:main.vaccine_efficacy": 0.85,
            "J:main.relative_contact_rate": 0.45,
            "J:main.s_n": 1000,
            "J:main.v_n": 0,
            "J:main.i_n": 1,
            "J:main.i_v_n": 0,
            "J:main.r_n": 0,
        },
        "outputs": [
            "P:main.out.S",
            "P:main.out.E",
            "P:main.out.I",
            "P:main.out.R",
            "P:main.out.V",
        ],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "code": 200,
        "result": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "P:main.out.E": [
                    1,
                    73.95817522828585,
                    299.4813761732133,
                    382.57161098064415,
                    0.0,
                ],
                "P:main.out.I": [
                    1,
                    40.77946378271174,
                    69.45877436716297,
                    19.550333583051962,
                    3.369246624335182,
                ],
                "P:main.out.R": [
                    0,
                    29.69380194651054,
                    211.0451150975806,
                    352.2147278757421,
                    391.94368106215154,
                ],
                "P:main.out.S": [
                    1000,
                    487.999750917069,
                    137.4377460493456,
                    45.93570973719449,
                    21.97584305388535,
                ],
                "P:main.out.V": [
                    0,
                    439.04207385464514,
                    564.0808777774411,
                    572.4926792821614,
                    580.8429534496793,
                ],
            },
        },
        "status": "success",
    }

    assert result == expected
