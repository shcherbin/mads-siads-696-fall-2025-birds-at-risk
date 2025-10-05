import os
import pandas as pd
import polars as pl

from birds.settings import load_settings

settings = load_settings()

class IUCNDataTables:
	SCHEMA = pl.Schema({
		'assessmentId': pl.Utf8,
		'internalTaxonId': pl.Utf8,
		'scientificName': pl.Utf8,
		'redlistCategory': pl.Utf8,
		'redlistCriteria': pl.Utf8,
		'yearPublished': pl.Int32,
		'assessmentDate': pl.Utf8,
		'criteriaVersion': pl.Utf8,
		'language': pl.Utf8,
		'rationale': pl.Utf8,
		'habitat': pl.Utf8,
		'threats': pl.Utf8,
		'population': pl.Utf8,
		'populationTrend': pl.Utf8,
		'range': pl.Utf8,
		'useTrade': pl.Utf8,
		'systems': pl.Utf8,
		'conservationActions': pl.Utf8,
		'realm': pl.Utf8,
		'yearLastSeen': pl.Utf8,
		'possiblyExtinct': pl.Utf8,
		'possiblyExtinctInTheWild': pl.Utf8,
		'scopes': pl.Utf8,
	})

	def __init__(self):
		self.__settings = load_settings()
		self.__assessments_df = None

	@property
	def assessments(self) -> pd.DataFrame:
		if self.__assessments_df is None:
			assessments_path = os.path.join(self.__settings.redlist_species_data_path, 'assessments.csv')
			self.__assessments_df = pd.read_csv(assessments_path, header=0)
		return self.__assessments_df



