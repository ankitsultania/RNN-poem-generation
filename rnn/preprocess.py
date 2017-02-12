import numpy as np
import theano
import theano.tensor as T
import lasagne

#sys.stdout=open("log2.txt","w")
print "Hello"
in_text = open('mahabharata.txt', 'r').read()
in_text = in_text.decode("utf-8-sig")
chars = list(set(in_text))
data_size, vocab_size = len(in_text), len(chars)
char_to_ix = { ch:i for i,ch in enumerate(chars) }
ix_to_char = { i:ch for i,ch in enumerate(chars) }
lasagne.random.set_rng(np.random.RandomState(1))
LR = .01
CLIP = 100
FREQ = 500
LEN = 10
HIDDEN_SIZE = 300
EPOCHS = 50
BATCH_SIZE = 128

def make(p, batch_size = BATCH_SIZE, data=in_text, return_target=True):
    x = np.zeros((batch_size,LEN,vocab_size))
    y = np.zeros(batch_size)

    for n in range(batch_size):
        ptr = n
        for i in range(LEN):
            x[n,i,char_to_ix[data[p+ptr+i]]] = 1.
        if(return_target):
            y[n] = char_to_ix[data[p+ptr+LEN]]
    return x, np.array(y,dtype='int32')

def try_it_out(N=530):
    assert(len(seed_string)>=LEN)
    sample_ix = []
    x,_ = make(len(seed_string)-LEN, 1, seed_string,0)
    for i in range(N):
        ix = np.random.choice(np.arange(vocab_size), p=probs(x).ravel())
        sample_ix.append(ix)
        x[:,0:LEN-1,:] = x[:,1:,:]
        x[:,LEN-1,:] = 0
        x[0,LEN-1,sample_ix[-1]] = 1. 
    random_snippet = seed_string + ''.join(ix_to_char[ix] for ix in sample_ix)   
    random_snippet2=random_snippet.encode('utf-8')
    print("----\n %s \n----" % random_snippet2)

def main(EPOCHS=EPOCHS):
    seed_string = "**********"
    print "Start lasagne layers"
    l_in = lasagne.layers.InputLayer(shape=(None, None, vocab_size))
    l_forward_1 = lasagne.layers.LSTMLayer(
        l_in, HIDDEN_SIZE, grad_clipping=CLIP,
        nonlinearity=lasagne.nonlinearities.tanh)
    l_forward_2 = lasagne.layers.LSTMLayer(
        l_forward_1, HIDDEN_SIZE, grad_clipping=CLIP,
        nonlinearity=lasagne.nonlinearities.tanh)
    l_forward_slice = lasagne.layers.SliceLayer(l_forward_2, -1, 1)
    l_out = lasagne.layers.DenseLayer(l_forward_slice, num_units=vocab_size, W = lasagne.init.Normal(), nonlinearity=lasagne.nonlinearities.softmax)
    target_values = T.ivector('target_output')    
    network_output = lasagne.layers.get_output(l_out)
    cost = T.nnet.categorical_crossentropy(network_output,target_values).mean()
    all_params = lasagne.layers.get_all_params(l_out,trainable=True)
    print "Start calculating updates"
    updates = lasagne.updates.adagrad(cost, all_params, LR)
    print "Start compiling functions"
    train = theano.function([l_in.input_var, target_values], cost, updates=updates, allow_input_downcast=True)
    error = theano.function([l_in.input_var, target_values], cost, allow_input_downcast=True)
    probs = theano.function([l_in.input_var],network_output,allow_input_downcast=True)
   
    print "Start training"
    p=0
    try:
        for it in xrange(data_size * EPOCHS / BATCH_SIZE):
            try_it_out() # Generate text using the p^th character as the start. 
            
            avg_cost = 0;
            for _ in range(FREQ):
                x,y = make(p)
                
                #print(p)
                p += LEN + BATCH_SIZE - 1 
                if(p+BATCH_SIZE+LEN >= data_size):
                    print('Carriage Return')
                    p = 0;
                

                avg_cost += train(x, y)
            print("Epoch {} average loss = {}".format(it*1.0*FREQ/data_size*BATCH_SIZE, avg_cost / FREQ))
                    
    except KeyboardInterrupt:
        pass
    
if __name__ == '__main__':
    main()