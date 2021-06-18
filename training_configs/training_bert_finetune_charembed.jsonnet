// V14
{
  "dataset_reader": {
    "type": "conll2003onlyner",
    "tag_label": "ner",
    "coding_scheme": "IOB1",
    "max_length": std.parseInt(std.extVar("MAX_LENGTH")),
    "token_indexers": {
      "bert": {
          "type": "bert-pretrained",
          "pretrained_model": std.extVar("PRETRAINED_VOCAB_LOCATION"),
          "do_lowercase": false,
          "use_starting_offsets": true,
          # "max_pieces": std.parseInt(std.extVar("MAX_LENGTH")),
          "truncate_long_sequences": false,
      },
      "token_characters": {
        "type": "characters",
        "min_padding_length": 3
      }
    }
  },
  "train_data_path": std.extVar("TRAINING_DATA_PATH"),
  "validation_data_path": std.extVar("VALIDATION_DATA_PATH"),
  "model": {
    "type": "bert_crf_tagger",
    "label_encoding": "BIO",
    "constrain_crf_decoding": true,
    "calculate_span_f1": true,
    "dropout": 0.1,
    "include_start_end_transitions": false,
    "text_field_embedder": {
        "allow_unmatched_keys": true,
        "embedder_to_indexer_map": {
            "bert": ["bert", "bert-offsets"],
            "token_characters": ["token_characters"],
        },
        "token_embedders": {
            "bert": {
                "type": "bert-pretrained",
                "pretrained_model": std.extVar("PRETRAINED_MODEL_LOCATION"),
                "requires_grad": true,
                "top_layer_only": true,
                # "max_length": std.parseInt(std.extVar("MAX_LENGTH")),
            },
            "token_characters": {
                "type": "character_encoding",
                "embedding": {
                    "embedding_dim": 16
                },
                "encoder": {
                    "type": "cnn",
                    "embedding_dim": 16,
                    "num_filters": 128,
                    "ngram_filter_sizes": [3],
                    "conv_layer_activation": "relu"
                }
            }
        }
    }
  },
  # "iterator": {
  #   "type": "bucket",
  #   "sorting_keys": [["tokens", "num_tokens"]],
  #   "batch_size": std.parseInt(std.extVar("BATCH_SIZE")),
  #   "cache_instances": true,
  #   "biggest_batch_first": true,
  #  },
   "iterator": {
    "type": "basic",
    "batch_size": std.parseInt(std.extVar("BATCH_SIZE"))
  },
  "trainer": {
    "optimizer": {
        "type": "bert_adam",
        "lr": std.extVar("LEARNING_RATE"),
        "parameter_groups": [
          [["bias", "LayerNorm.bias", "LayerNorm.weight", "layer_norm.weight"], {"weight_decay": 0.0}]
        ]
    },
    "validation_metric": "+precision-overall",
    "num_epochs": std.parseInt(std.extVar("NUM_EPOCHS")),
    "num_serialized_models_to_keep": 100,
    "should_log_learning_rate": true,
    "cuda_device": 0
  }
}
