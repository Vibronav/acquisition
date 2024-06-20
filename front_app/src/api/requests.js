import { useQuery } from 'react-query';
import axiosInstance from '../../axiosConfig';

const getConfig = async () => {
  const res = await axiosInstance.get('/parse_config');
  return res.data;
}
export const useConfig = () => {
  return useQuery('config', getConfig);
}
