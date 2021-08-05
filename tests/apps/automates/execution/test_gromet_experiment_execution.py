from automates.apps.automates.execute_driver import execute_gromet_experiment_json


def test_execute_sir_simple_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "easel", "source": {"model": '{"name": "SIR-simple"}'}},
        "start": 0,
        "end": 120.0,
        "step": 30.0,
        "domain_parameter": "dt",
        "parameters": {"beta": 0.9, "S": 1, "I": 1, "R": 1, "gamma": 1},
        "outputs": ["S", "I", "R"],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "body": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "I": [1.0, -20.0, -41.0, -62.0, -83.0],
                "R": [1, 31, 61, 91, 121],
                "S": [1.0, -8.0, -17.0, -26.0, -35.0],
            },
        },
        "status": 200,
    }

    assert expected == result


def test_execute_chime_sir_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "easel", "source": {"model": '{"name": "CHIME-SIR"}'}},
        "start": 0,
        "end": 120.0,
        "step": 30,
        "domain_parameter": "n_days",
        "parameters": {
            "growth_rate": 0.0,
            "beta": 0.0,
            "i_day": 17.0,
            "N_p": 3,
            "infections_days": 14.0,
            "relative_contact_rate": 0.05,
            "s_n": 200,
            "i_n": 1,
            "r_n": 1,
        },
        "outputs": ["S", "I", "E", "R"],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "body": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "E": [0.0, 0.0, 0.0, 0.0, 0.0],
                "I": [
                    0.0,
                    0.8933233135653156,
                    0.7806198884453974,
                    0.6712711762750359,
                    0.5693715755370689,
                ],
                "R": [
                    0.0,
                    2.965680650912271,
                    4.763081925816063,
                    6.3215644582752715,
                    7.652866183157096,
                ],
                "S": [
                    0.0,
                    198.14099603552242,
                    196.45629818573855,
                    195.00716436544968,
                    193.77776224130582,
                ],
            },
        },
        "status": 200,
    }

    assert result == expected
