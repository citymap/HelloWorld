import tensorflow as tf

# directory = "../../Documents/stockdata/data1/*.*"
directory = "datas/bidask.*"
file_names = tf.train.match_filenames_once(directory)
file_names_Queue = tf.train.string_input_producer(file_names)
init = (tf.local_variables_initializer())
print(file_names, file_names_Queue)

reader = tf.TextLineReader()
key, value = reader.read(file_names_Queue)

record_defaults = [[''], ['1.'], ['1.']]
col1, col2, col3 = tf.decode_csv(
    value, record_defaults=record_defaults, field_delim=',')
features = tf.concat([col2], 0)

# features = [col1, col2, col3, col4, col5, col6]

with tf.Session() as sess:
    sess.run(init)
    # print(type(sess.run(file_names)))
    # print(sess.run(file_names))
    # sess.run(file_names_Queue)

    # Start populating the filename queue.
    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(coord=coord)

    for i in range(8):
        # Retrieve a single instance:
        # print(sess.run([col1, col2, col3]))
        # print(sess.run(key))
        example, label = sess.run([features, col3])
        # print(example,label)
        print(sess.run(key))
        # print(sess.run(value))
    coord.request_stop()
    coord.join(threads)
