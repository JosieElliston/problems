#include <stdio.h>
#include <stdbool.h>
#include <time.h>
#include <stdlib.h>


const int INPUT_SIZE = 1;
const int LAYER_SIZES[] = {2, 2, 1};
const size_t LAYERS_COUNT = sizeof(LAYER_SIZES)/sizeof(LAYER_SIZES[0]);

int main()
{
    return 0;
}

struct Node
{
    float bias;
    float weights[];
};

struct Layer
{
    int size;
    struct Node nodes[];
};

struct Net
{
    float eval_cash;
    struct Layer layers[];
};

srand(time(NULL));
const int INIT_RANGE = 5;
float random()
{
    return INIT_RANGE * (.5 - (float)rand() / (float)RAND_MAX);
}

// runtime test of const bool randomize and bool randomize
// runtime test of doing this with an big ugly if for randomize
struct Node construct_node(int prev_size, bool randomize)
{
    float bias;
    if (randomize)
    {
       bias = random();
    } else {
        bias = 0;
    }
    float weights[prev_size];
    for (int weight_i = 0; weight_i < prev_size; weight_i++)
    {   
        if (randomize)
        {
            weights[weight_i] = random();
        } else {
            weights[weight_i] = 0;
        }
    }
    struct Node node = {bias};
    node.weights = weights;
    return node;
}

struct Layer construct_layer(int prev_size, int cur_size, bool randomize)
{   
    struct Node nodes[cur_size];
    for (int node_i = 0; node_i < cur_size; node_i++)
    {
        
    }
}

struct Net construct_net(bool randomize) {
    struct Layer layers[LAYERS_COUNT];
    for (int layer_i = 0; layer_i < LAYERS_COUNT; layer_i++)
    {
        struct Layer layer
        for (int node_i = )
    }
    return struct Net
    {
        0,
        {

        }
    };
}