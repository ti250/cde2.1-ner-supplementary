// NO CHAR
{
  "dataset_reader": {
    "type": "conll2003onlyner",
    "tag_label": "ner",
    "coding_scheme": "IOB1",
    "token_indexers": {
      "bert": {
          "type": "bert-pretrained",
          "pretrained_model": std.extVar("PRETRAINED_VOCAB_LOCATION"),
          "do_lowercase": false,
          "use_starting_offsets": true,
          "truncate_long_sequences": false,
      },
    }
  },
  "train_data_path": std.extVar("TRAINING_DATA_PATH"),
  "validation_data_path": std.extVar("VALIDATION_DATA_PATH"),
  "model": {
    "type": "crf_tagger",
    "label_encoding": "BIO",
    "constrain_crf_decoding": true,
    "calculate_span_f1": true,
    "dropout": 0.5,
    "include_start_end_transitions": false,
    "text_field_embedder": {
        "allow_unmatched_keys": true,
        "embedder_to_indexer_map": {
            "bert": ["bert", "bert-offsets"],
        },
        "token_embedders": {
            "bert": {
                "type": "bert-pretrained",
                "pretrained_model": std.extVar("PRETRAINED_MODEL_LOCATION")
            },
        }
    },
    "encoder": {
        "type": "lstm",
        "input_size": 768,
        "hidden_size": std.parseInt(std.extVar("HIDDEN_SIZE")),
        "num_layers": 2,
        "dropout": 0.5,
        "bidirectional": true
    },
  },
  "iterator": {
    "type": "basic",
    "batch_size": std.parseInt(std.extVar("BATCH_SIZE"))
  },
  "trainer": {
    "optimizer": {
        "type": "bert_adam",
        "lr": std.extVar("LEARNING_RATE")
    },
    "should_log_learning_rate": true,
    "validation_metric": "+precision-overall",
    "num_serialized_models_to_keep": 100,
    "num_epochs": std.parseInt(std.extVar("NUM_EPOCHS")),
    "grad_norm": 5.0,
    "patience": 25,
    "cuda_device": 0
  }
}
