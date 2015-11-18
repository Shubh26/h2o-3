from testlibs import common
from testlibs.gbm import create_model_gbm
from testlibs.gbm import ORDERS
from utils.se_functions import get_auto_configs
from utils import Constant

import sys

class GbmBasic:
    def __init__(self, tc_id, configs, driver, dataset_chars):
        #Init configs for model
        self.cfgs = configs
        self.tc_id = tc_id

        # Helpers
        self.wd = driver
        self.ds_chars = dataset_chars

        self.add_cfgs = dict(
            dataset_chars = self.ds_chars
        )

    def setup(self):
        #Setup dataset for create model
        print 'Start running testcase:', self.tc_id
        print 'Start import dataset...'
        print '---Import train dataset:'
        train_fn = self.ds_chars.get_filepath(self.cfgs[Constant.train_dataset_id])
        print 'train file path: ', train_fn
        common.import_parse_file(self.wd, dict(file_path = train_fn,
                                               destination_key = self.cfgs[Constant.train_dataset_id]),
                                 self.add_cfgs, self.cfgs[Constant.train_dataset_id])

        print '---Import validate dataset:'
        if '' == self.cfgs[Constant.validate_dataset_id].strip():
            print 'This testcase have no validate dataset'
        elif self.ds_chars.is_available(self.cfgs[Constant.validate_dataset_id]):
            validate_fn = self.ds_chars.get_filepath(self.cfgs[Constant.validate_dataset_id])
            print 'validate file path:', validate_fn
            common.import_parse_file(self.wd, dict(file_path = validate_fn,
                                                   destination_key = self.cfgs[Constant.validate_dataset_id]),
                                     self.add_cfgs, self.cfgs[Constant.validate_dataset_id])
        else:
            print 'Dataset %s is not available in dataset characteristic' % self.cfgs[Constant.validate_dataset_id]
            print 'Test case', self.tc_id,': invalid'
            raise Exception('Test case invalid')

        print 'Import dataset is successfully...'


    def test(self):
        #Build, predict model, get values and return result
        print 'Test now:'
        result_dict = dict( result = 'PASS', message = 'This tescase is passed', mse = '')
        result_dict['train_dataset_id'] = self.cfgs['train_dataset_id']
        result_dict['validate_dataset_id'] = self.cfgs['validate_dataset_id']
        try:
            print 'Start build model...'
            print 'Get distribution from file: '
            list_distribution = ['AUTO', 'gaussian', 'bernoulli', 'multinomial', 'poisson', 'gamma', 'tweedie']
            list_distribution_file = [self.cfgs['auto'], self.cfgs['gaussian'], self.cfgs['binomial'], self.cfgs['multinomial'], self.cfgs['poisson'], self.cfgs['gamma'], self.cfgs['tweedie']]
            print 'Get distribution from file Done'
            print 'set list_distribution'
            if 0 == list_distribution_file.count('x'):
                distribution = list_distribution[0]
            else:
                distribution = list_distribution[list_distribution_file.index('x')]
            print 'set distribution Done'
            print self.cfgs
            configs = get_auto_configs(ORDERS, self.cfgs)
            configs['response_column'] = self.ds_chars.get_data_of_column(self.cfgs[Constant.train_dataset_id], 'target'),
            configs['distribution'] = distribution
            print "Get auto config Done"

            create_model_gbm (self.wd, configs)
            print 'Model is built successfully...'

            print 'Start predict model...'
            if not self.cfgs['validate_dataset_id'].strip() == '':
                common.predict_file(self.wd, dict(frame_select = self.cfgs[Constant.validate_dataset_id]))
            else:
                common.predict_file(self.wd, dict(frame_select = self.cfgs[Constant.train_dataset_id]))
            print 'Predict model is successfully...'

            print '---Getting value after predict model:'
            result_dict['mse'] = common.get_values(self.wd, ['mse'])


            print 'Test case %s is passed' % self.tc_id
            return result_dict

        except Exception as e:
            result_dict['result']= 'FAIL'
            result_dict['message'] =  "Reason Failed: " + str(e.message)
            print 'Test case %s is falied' % self.tc_id
            return result_dict


    def clean_up(self):
        print 'clean up now...'


def unit_test():
    pass


if __name__ == '__main__':
    unit_test()

