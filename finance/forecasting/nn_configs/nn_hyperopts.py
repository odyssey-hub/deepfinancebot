from darts.utils.likelihood_models import GaussianLikelihood

rnn_conf_day_det = {
    "input_chunk_length": 10,
    "model": "LSTM",
    "n_rnn_layers": 4,
    "hidden_dim": 20,
    "dropout": 0.1,
    "batch_size": 16,
    "n_epochs": 12,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

rnn_conf_day_det1 = {
    "input_chunk_length": 10,
    "model": "LSTM",
    "n_rnn_layers": 3,
    "hidden_dim": 15,
    "dropout": 0.1,
    "batch_size": 16,
    "n_epochs": 10,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

rnn_conf_week_det = {
    "input_chunk_length": 4,
    "model": "GRU",
    "n_rnn_layers": 3,
    "hidden_dim": 15,
    "dropout": 0.1,
    "batch_size": 16,
    "n_epochs": 10,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

rnn_conf_day_prob = {
    "input_chunk_length": 10,
    "model": "LSTM",
    "n_rnn_layers": 4,
    "hidden_dim": 20,
    "dropout": 0.1,
    "batch_size": 16,
    "n_epochs": 12,
    "likelihood": GaussianLikelihood(),
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

rnn_conf_hour_det = {
    "input_chunk_length": 30,
    "model": "LSTM",
    "n_rnn_layers": 2,
    "hidden_dim": 30,
    "dropout": 0.1,
    "batch_size": 16,
    "n_epochs": 10,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

rnn_conf_hour_prob = {
    "input_chunk_length": 30,
    "model": "LSTM",
    "n_rnn_layers": 2,
    "hidden_dim": 30,
    "dropout": 0.1,
    "batch_size": 16,
    "n_epochs": 10,
    "likelihood": GaussianLikelihood(),
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

nhits_conf_day_det = {
    "input_chunk_length": 10,
    "num_stacks": 2,
    "num_blocks": 2,
    "num_layers": 4,
    "layer_widths": 128,
    "dropout": 0.1,
    "batch_size": 12,
    "activation": "ReLU",
    "n_epochs": 5,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

nhits_conf_day_det1 = {
    "input_chunk_length": 4,
    "num_stacks": 2,
    "num_blocks": 3,
    "num_layers": 2,
    "layer_widths": 512,
    "dropout": 0.2,
    "batch_size": 12,
    "activation": "ReLU",
    "n_epochs": 5,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

nhits_conf_day_prob = {
    "input_chunk_length": 10,
    "num_stacks": 2,
    "num_blocks": 2,
    "num_layers": 4,
    "layer_widths": 128,
    "dropout": 0.1,
    "batch_size": 12,
    "activation": "ReLU",
    "n_epochs": 5,
    "likelihood": GaussianLikelihood(),
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

nhits_conf_hour_det = {
    "input_chunk_length": 30,
    "num_stacks": 3,
    "num_blocks": 1,
    "num_layers": 4,
    "layer_widths": 64,
    "dropout": 0.2,
    "batch_size": 16,
    "activation": "ReLU",
    "n_epochs": 6,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

nhits_conf_hour_det1 = {
    "input_chunk_length": 10,
    "num_stacks": 1,
    "num_blocks": 2,
    "num_layers": 1,
    "layer_widths": 512,
    "dropout": 0.1,
    "batch_size": 16,
    "activation": "ReLU",
    "n_epochs": 8,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

nhits_conf_hour_prob = {
    "input_chunk_length": 30,
    "num_stacks": 3,
    "num_blocks": 1,
    "num_layers": 4,
    "layer_widths": 64,
    "dropout": 0.2,
    "batch_size": 16,
    "activation": "ReLU",
    "n_epochs": 6,
    "likelihood": GaussianLikelihood(),
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

tcn_conf_day_det = {
    "kernel_size": 10,
    "num_filters": 5,
    "dilation_base": 2,
    "weight_norm": True,
    "dropout": 0.2,
    "batch_size": 4,
    "n_epochs": 5,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

tcn_conf_day_prob = {
    "kernel_size": 10,
    "num_filters": 5,
    "dilation_base": 2,
    "weight_norm": True,
    "dropout": 0.2,
    "batch_size": 4,
    "n_epochs": 5,
    "likelihood": GaussianLikelihood(),
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

tcn_conf_hour_det = {
    "kernel_size": 25,
    "num_filters": 10,
    "dilation_base": 3,
    "weight_norm": True,
    "dropout": 0.2,
    "batch_size": 8,
    "n_epochs": 7,
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}

tcn_conf_hour_prob = {
    "kernel_size": 25,
    "num_filters": 10,
    "dilation_base": 3,
    "weight_norm": True,
    "dropout": 0.2,
    "batch_size": 8,
    "n_epochs": 7,
    "likelihood": GaussianLikelihood(),
    "pl_trainer_kwargs": {"enable_progress_bar": False},
    "random_state": 42
}
